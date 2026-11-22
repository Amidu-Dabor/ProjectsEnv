# Cookie Clicker Bot (Selenium)

A bot that plays the browser game [Cookie Clicker](https://orteil.dashnet.org/experiments/cookie/) on its own.

## How it works

- Opens the game in Chrome with Selenium and clicks the cookie continuously.
- Every 5 seconds, checks the store and buys the most expensive upgrade it can afford.
- After 5 minutes, stops and prints the cookies-per-second rate the bot reached.

## Tech

Python · Selenium WebDriver · Chrome

## Run

```bash
pip install selenium
python main.py
```
Update `chrome_driver_path` in `main.py`, or remove it on Selenium 4.6+, which finds the driver automatically.
