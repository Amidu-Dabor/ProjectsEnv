# Automated Birthday Wisher

Emails a personalised birthday message to anyone in `birthdays.csv` whose birthday is today. Run it daily, for example with cron.

## How it works

- Reads names, emails and birthdays from `birthdays.csv` with pandas.
- If today matches a birthday, picks one of three letter templates at random and fills in the name.
- Sends the letter through Gmail's SMTP server.

## Tech

Python · pandas · smtplib

## Run

Set these environment variables before running (never put keys in the code):

```
EMAIL_APP_PASSWORD=...   # a Gmail app password
```

Set `SENDER_EMAIL` in `main.py`, add people to `birthdays.csv`, and run `python main.py`.
