# Architecture

## Design goals

1. A player can reach and play every game with only a mouse.
2. Game rules remain independent from pygame so they are easy to test.
3. Algorithms solve real gameplay problems instead of adding artificial complexity.
4. New games plug into one small application shell.

## Layers

- **Domain models** contain rules, state, physics, and AI. They do not draw pixels.
- **Scenes** translate mouse events into domain operations and draw the current state.
- **Shared UI** provides buttons, headers, difficulty selection, pause, and sound controls.
- **Application services** own settings, scores, the game registry, and scene navigation.

## Object-oriented design

`Scene` is the only major inheritance hierarchy. Each scene implements the same event,
update, and draw lifecycle. Game models use composition: a game owns a board, scheduler,
physics model, or AI strategy. Difficulty swaps strategy objects without changing UI code.

## Coordinate system

All scenes draw to a logical 1280 x 720 canvas. The application scales that canvas to the
current window while preserving aspect ratio. Mouse coordinates are converted back into
logical coordinates before scenes receive them.

## State ownership

- `App` owns pygame, the window, settings, registry, and `SceneStack`.
- `SceneStack` owns the current navigation history.
- Each game scene owns exactly one game model.
- `SettingsStore` owns JSON persistence under `%LOCALAPPDATA%\GamesForGrandpa`.

