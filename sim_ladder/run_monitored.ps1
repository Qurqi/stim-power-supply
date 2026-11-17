# Runs LTspice netlists in batch mode and watches each run's progress.
# Progress = last simulated time stored in the .raw file (falls back to file growth).
# A run that makes no progress for -StallSec seconds is stopped and reported as STALLED.
# Usage:  .\run_monitored.ps1 -Nets a.net,b.net -MaxParallel 3 -Status P9_status.txt
param(
  [string[]]$Nets,
  [int]$MaxParallel = 3,
  [int]$CheckSec = 30,
  [int]$StallSec = 150,
  [int]$NoDataSec = 300,
  [int]$MaxMin = 45,
  [int]$StaggerSec = 25,
  [string]$Status = 'run_status.txt',
  [string]$LTspice = 'C:\Program Files\ADI\LTspice\LTspice.exe'
)

function Get-SimTime([string]$raw) {
  # returns last simulated time in seconds, -1 if no data yet, -2 if the header cannot be parsed
  if (-not (Test-Path -LiteralPath $raw)) { return -1 }
  try {
    $fs = New-Object System.IO.FileStream($raw, [System.IO.FileMode]::Open, [System.IO.FileAccess]::Read, [System.IO.FileShare]::ReadWrite)
  } catch { return -1 }
  try {
    $len = $fs.Length
    if ($len -lt 200) { return -1 }
    $n = [int][Math]::Min(32768, $len)
    $buf = New-Object byte[] $n
    [void]$fs.Read($buf, 0, $n)
    $txt = [System.Text.Encoding]::Unicode.GetString($buf)
    $i = $txt.IndexOf('Binary:')
    $m = [regex]::Match($txt, 'No\. Variables:\s*(\d+)')
    if ($i -lt 0 -or -not $m.Success) { return -2 }
    $nl = $txt.IndexOf("`n", $i)
    $off = [long](($nl + 1) * 2)
    $nv = [int]$m.Groups[1].Value
    $rec = 8 + 4 * ($nv - 1)
    $cnt = [long][Math]::Floor(($len - $off) / $rec)
    if ($cnt -lt 1) { return -1 }
    [void]$fs.Seek($off + ($cnt - 1) * $rec, [System.IO.SeekOrigin]::Begin)
    $tb = New-Object byte[] 8
    [void]$fs.Read($tb, 0, 8)
    return [Math]::Abs([BitConverter]::ToDouble($tb, 0))
  } finally { $fs.Close() }
}

function Say([string]$s) {
  $line = ('{0:HH:mm:ss}  {1}' -f (Get-Date), $s)
  Add-Content -LiteralPath $Status -Value $line -Encoding ascii
}

Set-Content -LiteralPath $Status -Value '' -Encoding ascii
$Nets = @($Nets | ForEach-Object { $_ -split ',' } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$queue = New-Object System.Collections.Queue
foreach ($n in $Nets) { $queue.Enqueue($n) }
$runs = @()
$t0 = Get-Date
while ($queue.Count -gt 0 -or @($runs | Where-Object { $_.State -eq 'RUNNING' }).Count -gt 0) {
  while ($queue.Count -gt 0 -and @($runs | Where-Object { $_.State -eq 'RUNNING' }).Count -lt $MaxParallel) {
    $n = $queue.Dequeue()
    $p = Start-Process -FilePath $LTspice -ArgumentList '-b', $n -PassThru
    $runs += [pscustomobject]@{ Net = $n; Proc = $p; State = 'RUNNING'; Start = Get-Date; LastT = -1.0; LastSize = 0L; LastMove = Get-Date }
    Say "START   $n"
    # LTspice instances launched at the same instant interfere with each other (only the last one runs properly),
    # so leave a gap before starting the next.
    Start-Sleep -Seconds $StaggerSec
  }
  Start-Sleep -Seconds $CheckSec
  foreach ($r in @($runs | Where-Object { $_.State -eq 'RUNNING' })) {
    $raw = [System.IO.Path]::ChangeExtension((Join-Path (Get-Location) $r.Net), '.raw')
    $t = Get-SimTime $raw
    $size = 0L
    if (Test-Path -LiteralPath $raw) { $size = (Get-Item -LiteralPath $raw).Length }
    $moved = ($t -gt ($r.LastT + 2e-6)) -or ($t -lt 0 -and $size -gt $r.LastSize)
    if ($moved) { $r.LastMove = Get-Date }
    $r.LastT = [Math]::Max($r.LastT, $t)
    $r.LastSize = $size
    $age = [int]((Get-Date) - $r.Start).TotalSeconds
    $idle = [int]((Get-Date) - $r.LastMove).TotalSeconds
    if ($r.Proc.HasExited) {
      $r.State = 'DONE'
      Say ("DONE    {0}  after {1} s" -f $r.Net, $age)
      continue
    }
    $tms = if ($t -ge 0) { '{0:N3} ms' -f ($t * 1000) } else { 'no data yet' }
    Say ("running {0}  sim time {1}  raw {2:N0} MB  wall {3} s  idle {4} s" -f $r.Net, $tms, ($size / 1MB), $age, $idle)
    $limit = if ($r.LastT -lt 0) { $NoDataSec } else { $StallSec }
    if ($idle -ge $limit) {
      try { Stop-Process -Id $r.Proc.Id -Force -Confirm:$false } catch {}
      $r.State = 'STALLED'
      Say ("STALLED {0}  at sim time {1}  (no progress for {2} s) - stopped" -f $r.Net, $tms, $idle)
    }
  }
  if (((Get-Date) - $t0).TotalMinutes -gt $MaxMin) {
    foreach ($r in @($runs | Where-Object { $_.State -eq 'RUNNING' })) {
      try { Stop-Process -Id $r.Proc.Id -Force -Confirm:$false } catch {}
      $r.State = 'TIMEOUT'
      Say ("TIMEOUT {0}" -f $r.Net)
    }
    break
  }
}
Say 'ALL FINISHED'
