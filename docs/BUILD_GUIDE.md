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

```powershell
uv run pytest tests/test_paddle_rally.py
```

**Expected result:** collisions are stable and AI speed/reaction differs by difficulty.

**Checkpoint:** `git checkout lesson-05-paddle-rally`

## Lesson 6: Release

**Goal:** Persist settings, package a portable Windows app, and automate releases.

**Concepts:** JSON serialization, defensive loading, CI, deterministic packaging.

```powershell
uv run ruff check .
uv run pytest
uv run games-for-grandpa --smoke-test
.\scripts\build.ps1
```

**Expected result:** `dist/GamesForGrandpa-windows.zip` contains a runnable application.

**Checkpoint:** `git checkout lesson-06-release`

## Reading a checkpoint

Use these commands to understand what changed:

```powershell
git log --oneline --decorate
git show --stat lesson-03-target-tap
git diff lesson-02-framework..lesson-03-target-tap
```

Read domain models before scenes. Models explain the rules; scenes mainly translate input
and render model state.
