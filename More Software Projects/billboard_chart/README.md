# Billboard Hot 100 Time Machine (Spotify)

Enter any date, and this builds a private Spotify playlist of the Billboard Hot 100 songs from that week.

## How it works

- Scrapes the song titles for the date from billboard.com with BeautifulSoup.
- Signs in to Spotify with OAuth (Spotipy) and searches for each song.
- Creates a private playlist and adds the songs it found.

## Tech

Python · requests · BeautifulSoup · Spotipy (Spotify Web API)

## Run

Set these environment variables before running (never put keys in the code):

```
SPOTIFY_CLIENT_SECRET=...
```

Set your `client_id` in `main.py`, then run:

```bash
pip install requests beautifulsoup4 spotipy
python main.py
```

The Spotify login token is cached in `token.txt`, which is git-ignored.
