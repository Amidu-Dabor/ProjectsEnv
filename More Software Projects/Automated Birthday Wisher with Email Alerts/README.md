# Motivational Quote Emailer

Emails a random motivational quote from `quotes.txt`, with the day of the week in the subject line. It's a first step towards the full Birthday Wisher.

## How it works

- Picks a random quote from `quotes.txt`.
- Sends it by email through Gmail's SMTP server.

## Tech

Python · smtplib

## Run

Set these environment variables before running (never put keys in the code):

```
EMAIL_APP_PASSWORD=...   # a Gmail app password
```

Set the sender and recipient addresses in `main.py`, then run `python main.py`.
