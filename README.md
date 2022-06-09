# **STORE SCRAPER**
Web scrapers to extract products data for:
- [Aldi](https://www.aldi.co.uk/)
- [Loblaw](https://www.loblaws.ca/)
- [Tesco](https://www.tesco.com/)
- [Woolworths](https://www.tesco.com/)
- [Wholefoodsmarket](https://www.wholefoodsmarket.com/products)
- [Kroger](https://www.kroger.com/)

Major info extracted for a product are: Name, Category, Subcategory, Product URL and ID. Other metas that maybe included are Price, Brand etc

### **Requirements**
- Python 3.6+
- Chrome Version 101.0.4951.64

### **Installation**
```
git clone https://github.com/atehe/stores_scraper.git
cd store_scrapers
pip install -r requirements.txt
```

### **Usage**
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
> Wholefoodsmarket and Loblaws store are region restrictive and will 
> require the region IP address of US and Canada respectively using a 
> VPN or proxy service.

> Continuous loading of pages crashes the browser in loblaw scraper due to 
> high ram usage so its preferable to run in a system with enough RAM.
> Uncommenting some code in the script can as well limit the amount of 
> pages loaded to prevent the browser from crashing.

> Kroger store blocks scraper after sometime but scraper is made to 
> close automatically when blocked and resumes from where it stopped when
> restarted(manually). For better performance a rotating proxy can be used.
> To run kroger scraper from the beginning delete the kroger folder in 
> utils

> Scrapers (browser) maybe sensitive to external input(keyboard or mouse 
> movements and clicks) for the first few minutes while extracting the  
> subcategories due to action needed like hover, clicking etc


