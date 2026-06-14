# Changelog

## v0.3.0 - 2026-06-14

### Added

- Added Connect Four with legal-column tracking and depth-limited minimax AI.
- Added Space Defense with mouse movement, automatic firing, enemy formation updates, and
  collision tests.
- Added Maze Chase with click-to-travel movement, pellet collection, and BFS enemy pathing.
- Added Whack-a-Mole, Target Practice, Memory Cards, Jigsaw Puzzle, and Fishing.
- Added paged Game Room browsing so the launcher stays large and readable with eleven games.
- Added pure model tests and screenshots for every new game.

### Changed

- Updated the roadmap around a larger v0.3 catalog release instead of spreading the same
  requested list across later versions.

## v0.2.2 - 2026-06-14

### Changed

- Removed the in-game Menu button and difficulty picker; games now show only Home and
  Sound On/Off during play.
- Result screens now show only the ending message plus Home and Restart.
- Renamed the launcher header to Game Room.
- Replaced the side-view Duck Hunt rifle with a smaller first-person shotgun-and-hands
  overlay.
- Made Duck Hunt faster and smaller, added ten hearts, and made escaped ducks cost one
  heart.
- Added a hit-duck sprite, gunshot sound, and quack sound.
- Fixed Tic Tac Toe to medium difficulty and Pong to easy difficulty in the player UI.

## v0.2.1 - 2026-06-14

### Changed

- Replaced the placeholder Duck Hunt rifle with an original transparent hunting shotgun
  sprite featuring realistic wood and metal materials.
- Rotated the shotgun toward the mouse using constant-time vector and angle calculations.
- Refreshed the Duck Hunt and launcher screenshots to show the upgraded artwork.

## v0.2.0 - 2026-06-14

### Changed

- Replaced Target Tap with a moving Duck Hunt game and visible rifle sight.
- Added a polished original mallard sprite with a larger accessible hit area.
- Renamed Three in a Row to Tic Tac Toe and Paddle Rally to Pong.
- Rebuilt the launcher with colorful full-card game screenshots and no instruction text.
- Replaced the five-button toolbar with two visible controls: Home and Menu.
- Moved restart, difficulty, sound, and pause behavior into the game menu.
- Replaced pygame's bitmap font with native TrueType typography.
- Restyled every game with a brighter, distinct, high-contrast visual theme.

## v0.1.0 - 2026-06-14

### Added

- Mouse-only launcher with large, high-contrast controls.
- Target Tap with bounded recent-position scheduling.
- Three in a Row with random, depth-limited, and full minimax opponents.
- Paddle Rally with collision physics and predictive AI.
- Persistent sound, difficulty, and best-score settings.
- Generated sound effects with no external media assets.
- Automated tests, headless scene smoke checks, screenshots, and Windows packaging.
- Sequential learning tags and rebuild documentation.
