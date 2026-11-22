# Send an SMS with Twilio

A minimal example of sending a text message with the Twilio API, including support for HTTP proxies.

## How it works

- Reads the Twilio credentials and proxy settings from environment variables.
- Sends one SMS and prints the message ID.

## Tech

Python · Twilio

## Run

Set these environment variables before running (never put keys in the code):

```
ACC_SID=...
AUTH_TOKEN=...
http_proxy=...    # only needed behind a proxy
https_proxy=...
```

Set the `from_` and `to` numbers in `main.py`, then run:

```bash
pip install twilio
python main.py
```
