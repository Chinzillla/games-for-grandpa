# Release Process

## Local verification

```powershell
uv sync --frozen
uv run ruff check .
uv run pytest
uv run games-for-grandpa --smoke-test
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

Extract `dist/GamesForGrandpa-windows.zip` into a new directory and run
`GamesForGrandpa.exe`. Verify Home, Pause, Continue, Restart, Sound, Difficulty, and every
game card using only the mouse.

## Publish

```powershell
git tag -a v0.2.1 -m "Games for Grandpa v0.2.1"
git push origin main --follow-tags
```

The tag starts `.github/workflows/release.yml`. It repeats all checks, builds on a clean
Windows runner, uploads the ZIP as a workflow artifact, and creates a public GitHub Release
with a SHA-256 checksum.

## Unsigned application warning

The first release is not code-signed. Windows SmartScreen may show a warning because the
executable is new and unsigned. Confirm the download came from this repository, compare the
ZIP checksum if desired, then choose **More info** and **Run anyway**.
