# Coffee & Wifi: Café Directory (Flask)

A small Flask website that lists cafés suitable for working, with ratings for coffee, Wi-Fi and power sockets, and a form for adding new ones.

## How it works

- `/`: home page.
- `/cafes`: a table of all cafés from `cafe-data.csv`.
- `/add`: a validated Flask-WTF form that appends a new café to the CSV.

## Tech

Python · Flask · Flask-WTF · WTForms · Flask-Bootstrap

## Run

Set these environment variables before running (never put keys in the code):

```
FLASK_SECRET_KEY=any-long-random-string
```

Then run:

```bash
pip install -r requirements.txt
python main.py
```

Open http://127.0.0.1:5000.
