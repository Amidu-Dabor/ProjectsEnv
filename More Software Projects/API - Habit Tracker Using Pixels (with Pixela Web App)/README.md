# Habit Tracker (Pixela)

Tracks a daily habit as a coloured "pixel" graph on [Pixela](https://pixe.la), through its REST API.

## How it works

- Creates a Pixela user and a graph.
- Posts today's value as a pixel, using today's date in `YYYYMMDD` format.
- Includes the update and delete requests for editing a day's pixel.

## Tech

Python · requests · Pixela API

## Run

Set these environment variables before running (never put keys in the code):

```
PIXELA_TOKEN=...
```

Change `USERNAME` and `GRAPH_ID` in `main.py`, then run `python main.py`.
