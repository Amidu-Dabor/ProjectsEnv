# Amazon Price Tracker

Scrapes the current price of an Amazon product page.

## How it works

- Requests the page with browser-like headers.
- Parses the price with BeautifulSoup and lxml, and prints it.
- Natural next step: compare it with a target price and send an email alert.

## Tech

Python · requests · BeautifulSoup · lxml

## Run

```bash
pip install requests beautifulsoup4 lxml
python main.py
```

> Amazon's page layout changes often, and it may block automated requests.
