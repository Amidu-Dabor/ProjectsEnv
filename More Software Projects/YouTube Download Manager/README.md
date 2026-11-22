# YouTube Download Manager (Kivy)

A desktop app for downloading YouTube videos: paste a link, check the video details, choose a resolution and download.

## How it works

- Built with Kivy and KivyMD for the interface.
- Uses `yt-dlp` to fetch video information and download it at the chosen resolution (480p by default).
- `buildozer.spec` holds the settings for packaging it as an Android app with Buildozer; `Brewfile` lists the macOS system packages.

## Tech

Python · Kivy · KivyMD · yt-dlp

## Run

```bash
pip install -r requirements.txt
python main.py
```

> Only download videos you have the right to download.
