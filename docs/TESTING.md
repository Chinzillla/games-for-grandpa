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
- Duck Hunt movement, flight scheduling, hit detection, escape/life loss, and scoring;
- every Tic Tac Toe winning line and all reachable player paths against Challenge AI;
- Connect Four legal columns, wins, draws, and computer replies;
- Pong reflection, prediction, clamping, collision, speed limits, and scoring;
- Space Defense movement, automatic shots, enemy collision, and loss states;
- Maze Chase pellet collection and BFS enemy pathing;
- Whack-a-Mole spawn scheduling and click scoring;
- Target Practice hit testing and moving-target reflection;
- Memory Cards pair matching;
- Jigsaw Puzzle swapping and solved detection;
- Fishing hook collision, reeling tension, break behavior, and catch completion;
- missing, corrupt, and valid persistence files;
- mouse-only navigation from Home into a game and back;
- the minimal Home/Sound HUD and result-screen restart behavior;
- paged Game Room behavior for all eleven game cards;
- rendering every scene for 1280 x 720 and 1920 x 1080 output;
- headless initialization and drawing of every registered game.

The packaging check extracts the release ZIP into a clean directory and confirms the bundled
`GamesForGrandpa.exe --smoke-test` exits successfully.

## Human play checklist

Automated checks do not replace play testing. Before sharing a release with the intended
player, spend at least ten minutes in each game and check:

- every action is possible without a keyboard;
- Home, Restart, and Sound remain easy to hit;
- text remains readable at the intended monitor resolution;
- generated sounds are comfortable;
- fixed per-game difficulty feels appropriate for the intended player;
- no game traps the player on a result screen;
- the unsigned SmartScreen instructions are understandable.
