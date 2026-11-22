# Mail Merge

Creates a personalised letter for every name in a list, the same idea as mail merge in Word.

## How it works

- Reads names from `Input/Names/invited_names.txt`.
- Replaces `[name]` in `Input/Letters/starting_letter.txt` with each name.
- Writes one letter per person to `Output/ReadyToSend/`.

## Tech

Python (standard library file handling)

## Run

```bash
python main.py
```
