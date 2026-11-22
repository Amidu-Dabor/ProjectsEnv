# Netflix Movies & TV Shows: Data Wrangling

Cleans and enriches the Netflix titles dataset (`netflix_titles.csv`) so it is ready for analysis, using a reusable `NetflixDataCleaner` class.

## Pipeline

1. **Load and explore:** structure, data types and missing values.
2. **Find issues:** missing directors, countries and dates, inconsistent formats and duplicates.
3. **Clean:** fills or flags missing values and standardises text and dates.
4. **Transform and enrich:** parses durations, splits genres and countries, and derives date features.
5. **Validate and export:** checks the result and writes `cleaned_netflix.csv`.

A full write-up is in `Data and AI - Netflix Data Wrangling.pdf`.

## Tech

Python · pandas · NumPy · statsmodels

## Run

Open `netflix_data_wrangling.ipynb` in Jupyter and run all cells from this folder.

*Built for the Data & AI programme at Cyber Shujaa, Kenya.*
