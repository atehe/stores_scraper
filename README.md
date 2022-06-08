# STORE SCRAPER

## Requirements
- Python 3.6+
- Chrome Version 101.0.4951.64

## Installation
```
git clone <git_url>
cd store_scrapers
pip install -r requirements.txt
```

## Usage
- Tesco Scraper
```
scrapy crawl tesco -o <output_csv>
```

- Aldi Scraper
```
python store_scrapers/scripts/aldi.py <output_csv>
```

- Loblaw Scraper
```
python store_scrapers/scripts/lowblaw.py <output_csv>
```

- Wholefoodsmarket Scraper(US)

Wholefoodsmarket(US) is not accessible by IP address outside US, thus will require a US proxy or VPN to scrape
```
python store_scrapers/scripts/wholefoodsmarket.py <output_csv>
```


- Woolworths Scraper
```
python store_scrapers/scripts/woolworths.py <output_csv>
```

- Kroger Scraper
```
python store_scrapers/scripts/kroger.py <output_csv>
```



