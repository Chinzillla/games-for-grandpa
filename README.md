# Games for Grandpa

An accessible, mouse-only collection of original desktop games written in Python.

The project is also a sequential learning portfolio for object-oriented programming,
data structures, algorithms, testing, packaging, and release automation.

![Games for Grandpa menu](docs/images/game-room.png)

## Included games

- **Target Tap:** click ten large targets with no penalty for missing.
- **Three in a Row:** play against random, depth-limited minimax, or full minimax AI.
- **Paddle Rally:** move one paddle with the mouse against speed-limited predictive AI.

## Run from source

Install Python 3.12 and `uv`, then run:

```powershell
uv sync
uv run games-for-grandpa
```

No keyboard input is required during play.

## Learn from the project

Start with [`docs/BUILD_GUIDE.md`](docs/BUILD_GUIDE.md), then use the annotated
`lesson-*` Git tags to rebuild each layer sequentially. Algorithm explanations live in
[`docs/DSA_GUIDE.md`](docs/DSA_GUIDE.md).

## Verify

```powershell
uv run ruff check .
uv run pytest
uv run games-for-grandpa --smoke-test
```

## Windows release

Download the portable ZIP from GitHub Releases, extract it, and open
`GamesForGrandpa.exe`. The first release is unsigned, so Windows SmartScreen may ask you to
confirm that you want to run it.

Release maintainers should follow [`docs/RELEASE.md`](docs/RELEASE.md).
