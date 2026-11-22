# Flight Deal Finder

Checks flight prices for the next six months and sends an SMS when a flight is cheaper than the target price stored in a Google Sheet.

## How it works

- `data_manager.py`: reads destinations and target prices from a Google Sheet through the Sheety API.
- `flight_data.py`: sets the search window, from tomorrow to six months ahead.
- `flight_search.py`: searches the Kiwi.com Tequila flight API for the cheapest matching flight.
- `notification_manager.py`: sends the deal by SMS with Twilio.
- `main.py`: runs the search and sends a message only when a deal beats the target price.

## Tech

Python · requests · Sheety API · Kiwi.com Tequila API · Twilio

## Run

Set these environment variables before running (never put keys in the code):

```
FLIGHT_SEARCH_API_KEY=...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

Then update the Sheety URL in `data_manager.py` and the phone numbers in `notification_manager.py`, and run:

```bash
pip install requests twilio python-dateutil
python main.py
```
