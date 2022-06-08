from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from selenium.webdriver.chrome.service import Service
from csv import writer
import logging, time
from aldi import click

logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


def get_subcategories(driver):
    """Returns a list of dictionaries containing the category, subcategory and subcategory URL"""

    driver.get("https://www.woolworths.com.au")

    WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//a[@aria-controls='categoryHeader-menu' and not(contains(text(), 'Specials')) and not(contains(text(), 'Front of Store'))]",
            )
        )
    )
    category_elements = driver.find_elements(
        by=By.XPATH,
        value="//a[@aria-controls='categoryHeader-menu' and not(contains(text(), 'Specials')) and not(contains(text(), 'Front of Store'))]",
    )

    subcategories_list = []
    logging.info(">>> Extracting categories, subcategories and URL...")
    for category_elem in category_elements:
        category = category_elem.text
        click(category_elem, driver)
        subcategory_elements = driver.find_elements(
            by=By.XPATH, value="//ul[@class='categoriesNavigation-list']//a"
        )
        for subcategory_elem in subcategory_elements:
            subcategory = subcategory_elem.text
            subcategory_url = subcategory_elem.get_attribute("href")
            logging.debug(
                {
                    "category": category,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )

            subcategories_list.append(
                {
                    "category": category,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )
    logging.info(">>> Subcategories extraction complete.")
    return subcategories_list


def extract_product_id(url):
    """Returns the product id from the product URL"""

    try:
        start_index = url.index("productdetails/") + 15
        end_index = url[start_index:].index("/")
        return url[start_index : start_index + end_index]
    except:
        return url


def extract_products(category, subcategory, page):
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

        logging.debug(
            f">>> {name}, {category}, {subcategory}, {price}, {cup_price}, {product_url}, {product_id}"
        )

        page_products.append(
            (name, category, subcategory, price, cup_price, product_url, product_id)
        )
    return page_products


def scrape_subcategory(driver, category, subcategory, subcategory_url, csv_writer):
    """Scrape subcategory products and writes to a csvfile"""
    driver.get(subcategory_url)

    page_num = 1
    continue_count = 0
    while True:
        logging.info(
            f">>> Extracting products from {category}: {subcategory} page {page_num}..."
        )
        try:
            # wait for products to load
            WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='shelfProductTile-information']")
                )
            )
        except:
            logging.critical(">>> Error while waiting. Retrying...")
            current_url = driver.current_url
            driver.get(current_url)

            # prevent unending error loop
            continue_count += 1
            if continue_count > 5:
                break
            continue

        try:
            next_page = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@class='paging-next ng-star-inserted']")
                )
            )
            last_page = False
        except:
            last_page = True

        page_products = extract_products(
            category, subcategory, driver.page_source.encode("utf-8")
        )

        csv_writer.writerows(page_products)

        page_num += 1

        if last_page:
            logging.info(f">>> {subcategory} scraping complete")
            break
        action = ActionChains(driver)
        action.move_to_element(to_element=next_page)
        action.click()
        action.perform()
        time.sleep(2)


def scrape_woolworths(driver, output_csv):
    subcategories_list = get_subcategories(driver)

    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = (
            "Name",
            "Category",
            "Subcategory",
            "Price",
            "Cup Price",
            "Product_URL",
            "Product_ID",
        )
        csv_writer.writerow(headers)

        for subcategory_dict in subcategories_list[83:]:
            category = subcategory_dict["category"]
            subcategory = subcategory_dict["subcategory"]
            subcategory_url = subcategory_dict["subcategory_url"]

            scrape_subcategory(
                driver, category, subcategory, subcategory_url, csv_writer
            )


if __name__ == "__main__":
    # driver configs
    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()  # more products are rendered in bigger window
    scrape_woolworths(driver, "wooly.csv")


## frozen seafood https://www.woolworths.com.au/shop/browse/freezer/frozen-seafood
