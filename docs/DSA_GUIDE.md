# Data Structures and Algorithms Guide

This guide explains where each structure or algorithm earns its place in the game.
Source comments beginning with `# DSA:` point back to these ideas.

## Application shell

### Scene stack

Navigation uses a Python list as a stack. The last scene is the active scene. `append`
pushes a scene and `pop` returns to the previous scene. Both operations are amortized O(1).
This matches menu -> game -> pause navigation naturally.

### Game registry

A dictionary maps stable game IDs to `GameDefinition` objects. Looking up a selected game
is average O(1), and adding a game does not require a large conditional statement.

### Finite-state machines

Enums represent a small set of valid states, such as PLAYING, PAUSED, and COMPLETE. This
prevents contradictory Boolean combinations and makes transitions explicit.

## Duck Hunt

The duck has continuous position and velocity values. Each frame updates those vectors and
reflects velocity at the flight boundaries in O(1). A list stores reusable flight patterns,
while a bounded `deque` remembers the three most recent pattern indices so new ducks do not
repeat the same route.

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

## Persistence

Settings and scores are dictionaries serialized as JSON. Reading and writing are O(n) in the
small document size. Invalid files fall back to safe defaults instead of preventing startup.
