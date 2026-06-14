$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$uvCommand = Get-Command uv -ErrorAction SilentlyContinue
if ($uvCommand) {
    $uv = $uvCommand.Source
} else {
    $uv = Get-ChildItem `
        "$env:LOCALAPPDATA\Microsoft\WinGet\Packages\astral-sh.uv_*" `
        -Recurse `
        -Filter uv.exe `
        -ErrorAction SilentlyContinue |
        Select-Object -First 1 -ExpandProperty FullName
}

if (-not $uv) {
    throw "uv was not found. Install it from https://docs.astral.sh/uv/."
}

$appDirectory = Join-Path $root "dist\GamesForGrandpa"
$zipPath = Join-Path $root "dist\GamesForGrandpa-windows.zip"
$checksumPath = "$zipPath.sha256"
$buildDirectory = Join-Path $root "build\GamesForGrandpa"

foreach ($path in @($appDirectory, $buildDirectory, $zipPath, $checksumPath)) {
    if (Test-Path -LiteralPath $path) {
        Remove-Item -LiteralPath $path -Recurse -Force
    }
}

& $uv run pyinstaller `
    --noconfirm `
    --clean `
    --onedir `
    --windowed `
    --name GamesForGrandpa `
    --paths src `
    src/games_for_grandpa/__main__.py

Copy-Item README.md, LICENSE -Destination $appDirectory
Copy-Item docs/BUILD_GUIDE.md, docs/DSA_GUIDE.md -Destination $appDirectory

Compress-Archive -Path "$appDirectory\*" -DestinationPath $zipPath -CompressionLevel Optimal
$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $zipPath).Hash.ToLowerInvariant()
"$hash  GamesForGrandpa-windows.zip" | Set-Content -Encoding ascii $checksumPath

Write-Host "Built $zipPath"
Write-Host "SHA-256: $hash"

