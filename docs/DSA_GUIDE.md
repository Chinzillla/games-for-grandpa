# Data Structures and Algorithms Guide

This guide explains where each structure or algorithm earns its place in the game.
Source comments beginning with `# DSA:` point back to these ideas.

## Application shell

### Scene stack

Navigation uses a Python list as a stack. The last scene is the active scene. `append`
pushes a scene and `pop` returns to the previous scene. Both operations are amortized O(1).
This matches game room -> game navigation naturally.

### Game registry

A dictionary maps stable game IDs to `GameDefinition` objects. Looking up a selected game
is average O(1), and adding a game does not require a large conditional statement.

### One-screen launcher

The Gameroom stores registered games in a list and maps each list index to a grid position.
Rendering the launcher is O(n) in the number of games, which is small enough for a single
screen. The stable game registry remains a dictionary so launching a selected game is still
average O(1).

### Finite-state machines

Enums represent a small set of valid states, such as PLAYING, HIT, COMPLETE, and GAME_OVER.
This prevents contradictory Boolean combinations and makes transitions explicit.

## Duck Hunt

The duck has continuous position and velocity values. Each frame updates those vectors and
checks escape bounds in O(1). Escaped ducks subtract one life; the finite-state machine ends
the round when lives reach zero. Score is unbounded, and the spawn speed scales from the
current score with an upper cap. A list stores reusable flight patterns, while a bounded
`deque` remembers the three most recent pattern indices so new ducks do not repeat the same
route.

## Tic Tac Toe

The board is a fixed nine-element list. A set tracks legal moves for O(1) average membership
and removal. Minimax recursively explores future moves. Alpha-beta pruning skips branches
that cannot affect the result. A dictionary memoizes repeated board states.

The full search is practical because the game tree is small. Easy uses a random legal move,
Normal limits search depth, and Challenge searches to terminal states.

## Pong

Positions and velocities are two-dimensional vectors. Rectangle intersection detects paddle
collisions. Reflection reverses the relevant velocity component. Challenge AI predicts where
the ball reaches its side and repeatedly reflects the predicted Y coordinate into the play
area. Each prediction is O(1).

## Connect Four

The board is a flat 42-cell array indexed by row and column. A set tracks columns that can
still accept a piece, giving average O(1) membership checks. Winner detection scans fixed
four-cell windows across four directions. The computer uses depth-limited minimax with
alpha-beta pruning and a small board-evaluation function that scores open four-cell windows.
The scene animates player and computer drops separately, but the model remains the source of
truth for legal columns and AI decisions.

## Space Defense

Active enemies, player bullets, enemy bolts, and shields are stored in lists because the
object counts are intentionally small. Each frame updates positions and checks rectangle
overlaps. This is O(e * b + s * b) for enemy, shield, and bullet counts, which is acceptable
for the fixed wave size and keeps the logic easy to read. A dictionary selects the lowest
living enemy in each column so only front-row ships fire.

## Maze Chase

The maze is a grid. Pellets live in a set so collecting one is average O(1). The enemy uses
breadth-first search over neighboring grid cells to find the shortest path through an
unweighted maze. BFS is O(V + E), where V is the number of walkable tiles and E is the number
of neighbor links.

## Whack-a-Mole

The model stores valid holes in a list and keeps recently used holes in a bounded `deque`.
That prevents repetitive spawns while keeping append and discard operations O(1). The latest
hit hole is stored as a nullable index so the scene can draw dizzy feedback in O(1).

## Memory Cards

Cards are a list of visual IDs. The visible grid index maps directly to a card in O(1), and
row/column arithmetic derives the current grid layout from the selected size. Matching two
selected indices compares their visual IDs and either marks them matched or turns them back
over.

## Jigsaw Puzzle

A shuffled tray list stores unplaced piece IDs. A board-slot list maps each solved slot to
either `None` or the source piece ID placed there. Correct drops remove a piece from the tray,
write it into the slot, and scan the board for completion in O(n), where n is at most 25.

## Persistence

Settings and scores are dictionaries serialized as JSON. Reading and writing are O(n) in the
small document size. Invalid files fall back to safe defaults instead of preventing startup.
