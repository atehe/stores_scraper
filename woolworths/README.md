# WOOLWORTHS SCRAPER

## Usage
The woolworths scraper can be run from the script or the command line using
```
python3 woolworths.py
```

## Process
The main function, `scrape_woolworths()` generates a dictionary containing the woolworths categories and their url and scrapes the products for each category into respective csv files.

It then combines them as into one csv with the `merge_csv()` function.

Using the `scrape_woolworths()` function it takes about 15hrs for the scraper to complete the scraping process of all categories. This can be reduced by lowering the wait-time for pages to load in `time.sleep()`

A single category can be scraped using the `scrape_category()` function in the scraper and passing in the required arguments.



