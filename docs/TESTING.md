# Testing and Acceptance

## Automated checks

Run:

```powershell
uv run ruff check .
uv run pytest
uv run games-for-grandpa --smoke-test
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

The suite verifies:

- scene-stack, registry, viewport, and mouse-button behavior;
- all Target Tap scheduling and scoring rules;
- every Three in a Row winning line and all reachable player paths against Challenge AI;
- Paddle Rally reflection, prediction, clamping, collision, speed limits, and scoring;
- missing, corrupt, and valid persistence files;
- mouse-only navigation from Home into a game and back;
- rendering every scene for 1280 x 720 and 1920 x 1080 output;
- headless initialization and drawing of every registered game.

The packaging check extracts the release ZIP into a clean directory and confirms the bundled
`GamesForGrandpa.exe --smoke-test` exits successfully.

## Human play checklist

Automated checks do not replace play testing. Before sharing a release with the intended
player, spend at least ten minutes in each game and check:

- every action is possible without a keyboard;
- Home, Pause, Continue, Restart, Sound, and Difficulty remain easy to hit;
- text remains readable at the intended monitor resolution;
- generated sounds are comfortable;
- Easy difficulty feels forgiving;
- no game traps the player on a result screen;
- the unsigned SmartScreen instructions are understandable.

