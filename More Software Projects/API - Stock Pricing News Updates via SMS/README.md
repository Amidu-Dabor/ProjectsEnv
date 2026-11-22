# Stock Price Alert with News (SMS)

Watches a stock (Tesla by default). When its closing price changes between the last two trading days, it texts you the change (🔺 up or 🔻 down) with a related news headline and summary.

## How it works

- Gets daily prices from the Alpha Vantage API and works out the percentage change.
- Fetches recent articles about the company from News API.
- Sends the change and a headline by SMS with Twilio.

## Tech

Python · requests · Alpha Vantage API · News API · Twilio

## Run

Set these environment variables before running (never put keys in the code):

```
ALPHAVANTAGE_API_KEY=...
NEWS_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

Then run:

```bash
pip install requests twilio
python main.py
```
