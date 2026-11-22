# Turtle Crossing Game

A Frogger-style arcade game: guide the turtle across a road full of moving cars. Each successful crossing raises the level and the cars' speed.

## How it works

- `player.py`: the turtle, moved up with the arrow key; it resets on reaching the finish line.
- `car_manager.py`: spawns randomly coloured cars and speeds them up each level.
- `scoreboard.py`: shows the level and the game-over message.
- `main.py`: the game loop and collision detection.

## Tech

Python · turtle (standard library)

## Run

```bash
python main.py
```
Press **Up** to move.
