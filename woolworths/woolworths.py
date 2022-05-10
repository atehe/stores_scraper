from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import logging
import time
import csv

logging.basicConfig(level=logging.INFO)
driver_path = "../utils/chromedriver"


def get_categories(driver):
    """Returns the a dictionary of the category an their url"""

    driver.get("https://www.woolworths.com.au")

    WebDriverWait(driver, 60).until(
        EC.visibility_of_all_elements_located(
            (
                By.XPATH,
                "//a[@aria-controls='categoryHeader-menu' and not(contains(text(), 'Specials'))]",
            )
        )
    )
    category_elements = driver.find_elements(
        by=By.XPATH,
        value="//a[@aria-controls='categoryHeader-menu' and not(contains(text(), 'Specials'))]",
    )
    category_dict = {}
    logging.info("Getting Categories and URL")
    for element in category_elements:
        url = element.get_attribute("href")
        category = element.text
        category_dict[category] = url
    return category_dict


def extract_product_id(url):
    """Returns the product id from the product URL"""

    try:
        start_index = url.index("productdetails/") + 15
        end_index = url[start_index:].index("/")
        return url[start_index : start_index + end_index]
    except:
        return url


def extract_products(category, page):
    """Returns list of tuples containing the product details in a page"""

    page_response = Selector(text=page)
    products = page_response.xpath("//div[@class='shelfProductTile-information']")

    page_products = []
    for product in products:
        name = "".join(
            product.xpath(
                ".//a[@class='shelfProductTile-descriptionLink']//text()"
            ).getall()
        )
        url = product.xpath(
            ".//a[@class='shelfProductTile-descriptionLink']/@href"
        ).get()
        price_dollar = (
            product.xpath(".//span[@class='price-dollars']/text()").get() or 0
        )
        price_cent = product.xpath(".//span[@class='price-cents']/text()").get() or 0

        cup_price = product.xpath(
            ".//div[contains(@class,'shelfProductTile-cupPrice')]/text()"
        ).get()
        price = ".".join([str(price_dollar), str(price_cent)])
        product_url = f"http://www.woolworths.com.au{url}"
        product_id = extract_product_id(url)

        page_products.append(
            (name, category, price, cup_price, product_url, product_id)
        )
    return page_products


def parse_category(driver, category, file):
    """Scrape a category and outputs it in file"""

    logging.info(f"{category.upper()} SCRAPING")

    with open(file, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            ("Name", "Category", "Price", "Cup Price", "Product_URL", "Product_ID")
        )
        page_num = 1
        while True:
            logging.info(f"Extracting products from {category} page {page_num}...")
            try:
                next_page = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//a[@class='paging-next ng-star-inserted']")
                    )
                )
                last_page = False
            except:
                logging.info(f"Last page in {category}")
                last_page = True

            driver.implicitly_wait(25)  #  wait for products to load

            page_products = extract_products(
                category, driver.page_source.encode("utf-8")
            )
            writer.writerows(page_products)

            page_num += 1

            if last_page:
                break
            action = ActionChains(driver)
            action.move_to_element(to_element=next_page)
            action.click()
            action.perform()


def scrape_woolworths():
    driver = webdriver.Chrome()
    categories = get_categories(driver)

    for category, category_url in categories.items():
        driver.get(category_url)

        category_filename = f"{''.join(category.split())}_woolworths.csv"
        parse_category(driver, category, category_filename)


if __name__ == "__main__":
    scrape_woolworths()
