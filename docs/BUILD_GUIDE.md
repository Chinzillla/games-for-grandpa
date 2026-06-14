# Sequential Build Guide

This document is the rebuild path. Run all commands from the repository root in PowerShell.
Each `lesson-*` tag marks a complete checkpoint that can be checked out and studied.

## Prerequisites

Install Git, Python 3.12, and `uv`. Then verify:

```powershell
git --version
python --version
uv --version
```

If the Windows app alias hides Python, `uv` can still locate or install Python 3.12.

## Lesson 1: Bootstrap

**Goal:** Create a reproducible Python package and development environment.

**Concepts:** package metadata, dependency locking, virtual environments, linting.

```powershell
uv sync
uv run python --version
uv run ruff check .
```

**Expected result:** Python 3.12 is used, dependencies install, and Ruff passes.

**Checkpoint:** `git checkout lesson-01-bootstrap`

## Lesson 2: Framework

**Goal:** Build the pygame loop, scaled canvas, scene stack, registry, and shared controls.

**Concepts:** interfaces, stack data structure, dictionary registry, event loop, coordinates.

**Build order:** implement `Scene` and `SceneStack`, add the 1280 x 720 canvas and
coordinate conversion, create the dictionary game registry, then build `Button`,
`GameToolbar`, and `HomeScene`. Keeping this order makes each layer testable before the
next layer depends on it.

```powershell
uv run pytest
uv run games-for-grandpa --smoke-test
```

**Expected result:** the shell can open each registered scene using mouse events.

**Checkpoint:** `git checkout lesson-02-framework`

## Lesson 3: Target Tap

**Goal:** Build a complete click-target game.

**Concepts:** list-backed candidate pool, bounded deque, state machine.

**Build order:** create `TargetScheduler` and test recent-position avoidance, add
`TargetTapModel` and its hit detection, then connect the model to a scene. Notice that tests
can click logical coordinates without initializing a pygame window.

```powershell
uv run pytest tests/test_target_tap.py
uv run games-for-grandpa
```

**Expected result:** ten successful clicks complete a round; misses do not reduce score.

**Checkpoint:** `git checkout lesson-03-target-tap`

## Lesson 4: Three in a Row

**Goal:** Add a strategy game with three AI difficulty levels.

**Concepts:** array, set, recursion, minimax, alpha-beta pruning, memoization.

**Build order:** implement the fixed board and legal-move set, test every winning line, add
random and minimax strategy objects, then exhaustively explore every player path against the
Challenge strategy. Only after that proof passes should pygame drawing be added.

```powershell
uv run pytest tests/test_three_in_row.py
```

**Expected result:** rules are correct and Challenge AI cannot lose from reachable states.

**Checkpoint:** `git checkout lesson-04-three-in-row`

## Lesson 5: Paddle Rally

**Goal:** Add real-time physics and predictive opponent behavior.

**Concepts:** vectors, clamping, collision detection, reflection, strategy objects.

**Build order:** define paddle and ball data, test clamping and wall reflection, add
constant-time paddle collision, implement scoring, then introduce AI strategies. Test the
physics model with fixed time steps before drawing it in pygame.

```powershell
uv run pytest tests/test_paddle_rally.py
```

**Expected result:** collisions are stable and AI speed/reaction differs by difficulty.

**Checkpoint:** `git checkout lesson-05-paddle-rally`

## Lesson 6: Release

**Goal:** Persist settings, package a portable Windows app, and automate releases.

**Concepts:** JSON serialization, defensive loading, CI, deterministic packaging.

**Build order:** add a data store with corrupt-file tests, generate simple tones in memory,
exercise every scene in dummy SDL mode, package with PyInstaller, then let GitHub Actions run
the same checks and publish the resulting ZIP.

```powershell
uv run ruff check .
uv run pytest
uv run games-for-grandpa --smoke-test
powershell -ExecutionPolicy Bypass -File .\scripts\build.ps1
```

**Expected result:** `dist/GamesForGrandpa-windows.zip` contains a runnable application.

**Checkpoint:** `git checkout lesson-06-release`

## Lesson 7: UI Redesign and Duck Hunt

**Goal:** Replace the first prototype visuals with a colorful, simplified game room.

**Concepts:** TrueType font discovery, off-screen scene rendering, velocity, bounded
history, modal UI state, and backward-compatible IDs.

**Build order:** replace bitmap fonts, render real scene screenshots into launcher cards,
move secondary controls into a modal menu, replace Target Tap with `DuckHuntModel`, then
restyle Tic Tac Toe and Pong without changing their tested domain logic.

```powershell
uv run pytest tests/test_duck_hunt.py tests/test_ui.py tests/test_navigation.py
uv run games-for-grandpa
```

**Expected result:** the launcher shows screenshot cards, each game has only Home and Sound
visible during play, and the duck moves continuously until clicked.

**Checkpoint:** `git checkout lesson-07-ui-redesign`

## Lesson 8: Aiming Sprite

**Goal:** Replace a procedural rifle placeholder with a polished first-person transparent
sprite that still follows the mouse.

**Concepts:** alpha transparency, resource packaging, angle calculation, subtle sprite
rotation, and first-person overlay positioning.

**Build order:** add the transparent PNG to the package, load it through
`importlib.resources`, calculate cursor offset from the screen center, convert that offset
into a small angle with `atan2`, rotate the source sprite, then keep it anchored at the
bottom of the screen.

```powershell
uv run ruff check .
uv run pytest
uv run games-for-grandpa --smoke-test
uv run python scripts/capture_screenshots.py
```

**Expected result:** the wooden hunting shotgun remains anchored near the bottom of the
screen and points at the crosshair throughout the playable area.

**Checkpoint:** `git checkout lesson-08-rifle-art`

## Lesson 9: One-Click Game Flow

**Goal:** Remove the modal menu and make Duck Hunt more game-like without complicating the
controls.

**Concepts:** finite-state machine, fixed scene difficulty, O(1) bounds checks, result
actions, generated audio, and transparent reaction sprites.

**Build order:** simplify `GameHud` to Home and Sound, move Home/Restart into result
screens, fix scene difficulties, add Duck Hunt lives and escape events, add gunshot/quack
effects, then refresh screenshots.

```powershell
uv run pytest tests/test_duck_hunt.py tests/test_ui.py tests/test_navigation.py
uv run games-for-grandpa --smoke-test
```

**Expected result:** games require no menu choices, Duck Hunt shows ten hearts, escaped ducks
cost hearts, and result screens expose only Home and Restart.

**Checkpoint:** `git checkout lesson-09-simple-flow`

## Reading a checkpoint

Use these commands to understand what changed:

```powershell
git log --oneline --decorate
git show --stat lesson-03-target-tap
git diff lesson-02-framework..lesson-03-target-tap
```

Read domain models before scenes. Models explain the rules; scenes mainly translate input
and render model state.
