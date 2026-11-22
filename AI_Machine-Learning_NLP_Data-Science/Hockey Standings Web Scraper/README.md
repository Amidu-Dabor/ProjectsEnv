# Hockey Standings Web Scraper

Scrapes NHL team statistics from the practice site [scrapethissite.com](https://www.scrapethissite.com/pages/forms/), cleans them and produces a summary table and charts.

## How it works

A `HockeyScraper` class:
1. Fetches the page, retrying up to 3 times with a delay.
2. Parses the stats table with BeautifulSoup.
3. Converts numeric columns and analyses wins, losses and goal differences.
4. Prints a summary table, saves a timestamped CSV to `hockey_data/` and saves charts to `hockey_data/visualizations/`.

Logging is built in, so failed requests and parsing problems are reported clearly.

## Tech

Python · requests · BeautifulSoup · pandas · Matplotlib · Seaborn · tabulate

## Run

Open `web_scraping.ipynb` in Jupyter and run all cells (`pip install requests beautifulsoup4 tabulate`).

A full write-up is in `Hockey Standings Web Scraper Project Report.pdf`.
