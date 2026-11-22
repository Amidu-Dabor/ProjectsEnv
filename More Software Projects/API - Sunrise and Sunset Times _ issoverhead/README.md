# ISS Overhead Notifier

Emails you when the International Space Station is passing over your location **and** it is dark enough to see it.

## How it works

- `iss_api()`: gets the ISS's current position from the Open Notify API.
- `sunrise_sunset_api()`: gets today's sunrise and sunset times for your coordinates.
- `is_iss_overhead()` and `is_night()`: check that the ISS is within ±5° of you and that it is night.
- If both are true, sends an email over SMTP. The script checks every 60 seconds.

## Tech

Python · requests · smtplib · Open Notify API · Sunrise-Sunset API

## Run

Set these environment variables before running (never put keys in the code):

```
EMAIL_APP_PASSWORD=...   # a Gmail app password, not your account password
```

Set `MY_LAT`, `MY_LONG` and `SENDER_EMAIL` in `main.py`, then run `python main.py`.
