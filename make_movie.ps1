$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

$Fps = if ($env:FPS) { [int]$env:FPS } else { 30 }

New-Item -ItemType Directory -Force -Path "movie" | Out-Null

$Frames = Get-ChildItem "frames/frame*.png" | Sort-Object Name
if ($Frames.Count -eq 0) {
    throw "No PNG frames found in frames/."
}

ffmpeg -y `
    -framerate $Fps `
    -pattern_type glob `
    -i "frames/frame*.png" `
    -c:v libx264 `
    -crf 18 `
    -pix_fmt yuv420p `
    -movflags +faststart `
    "movie/navier-stokes-vortex-lab.mp4"

Write-Host "Created movie/navier-stokes-vortex-lab.mp4"
