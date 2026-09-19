$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$NFrames = if ($env:NFRAMES) { [int]$env:NFRAMES } else { 240 }
$Width   = if ($env:WIDTH)   { [int]$env:WIDTH }   else { 1280 }
$Height  = if ($env:HEIGHT)  { [int]$env:HEIGHT }  else { 720 }

New-Item -ItemType Directory -Force -Path "frames" | Out-Null

if (-not (Test-Path "positions/frame0001.inc")) {
    Write-Host "Trajectory files not found; generating them first."
    python make_trajectories.py --frames $NFrames
}

povray fluid.pov `
    "+W$Width" "+H$Height" `
    "+KFI1" "+KFF$NFrames" `
    "+KI0" "+KF1" `
    "+FN" `
    "+A0.2" `
    "+Oframes/frame"

Write-Host "Finished. Rendered frames are in frames/."
