# Snake Game

The classic Snake game: eat food to grow, and avoid the walls and your own tail. Your best score is saved between games.

## How it works

- `snake.py`: the snake's body segments and movement (arrow keys).
- `food.py`: places food at random positions.
- `scoreboard.py`: the current score and the high score, saved in `high_score_file.txt`.
- `main.py`: the game loop and collision detection. The game resets instead of closing.

## Tech

Python · turtle (standard library)

## Run

```bash
python main.py
```
The earlier version, without a saved high score, is in `../Snake Game - Early Version/`.
