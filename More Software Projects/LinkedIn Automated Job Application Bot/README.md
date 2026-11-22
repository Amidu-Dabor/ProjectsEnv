# LinkedIn Easy Apply Bot (Selenium)

Automates applying to LinkedIn "Easy Apply" jobs from a search results page.

## How it works

- Signs in to LinkedIn with Selenium.
- Goes through the jobs in a saved search and opens each Easy Apply form.
- Fills in the phone number and submits single-step applications; multi-step ones are skipped.

## Tech

Python · Selenium WebDriver · Chrome

## Run

Fill in your details in place of the placeholders in `main.py` (better: load them from environment variables), set the job-search URL, then run:

```bash
pip install selenium
python main.py
```

> Automating LinkedIn may break its terms of service. Use this only as a learning example.
