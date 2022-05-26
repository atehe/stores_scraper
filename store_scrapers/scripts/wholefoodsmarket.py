from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aldi import click, excluded_keyword_in
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import logging, json, os, sys, time, random
from selenium import webdriver


logging.basicConfig(level=logging.INFO)


def load_all_products(driver):
    while True:
        try:
            load_more = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@aria-label='Load More Products']")
                )
            )
            click(load_more, driver)
        except:
            print("All products loaded")
            break
    return driver.page_source


# def handle_popup(driver):
#     popup = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH)))


def extract_products(category, subcategory, csv_writer, page):
    page_response = Selector(text=page.encode("utf8"))
    products = page_response.xpath("//div[@data-testid='product-tile']")

    for product in products:
        name = product.xpath(".//h2[@data-testid='product-tile-name']/text()").get()
        brand = product.xpath(".//span[@data-testid='product-tile-brand']/text()").get()
        product_url = product.xpath(
            ".//a[@data-testid='product-tile-link']/@href"
        ).get()
        ASIN = (
            product.xpath(
                ".//a[@data-testid='product-tile-link']/@data-csa-c-content-id"
            )
            .get()
            .strip("ASIN: ")
        )
        if not product_url.startswith("http"):
            product_url = f"https://www.wholefoodsmarket.com{product_url}"
        # regular_price = product.xpath(".//span[@class='regular_price']/b/text()").get()
        regular_price = "".join(
            product.xpath(".//li[@data-testid='regular-price']//text()").getall()
        )

        print((name, brand, category, subcategory, ASIN, regular_price, product_url))
        # csv_writer.writerow((name, brand, category, subcategory, regular_price))
        # TODO: write data with csv writer


def get_categories_dict(driver):
    driver.get("https://www.wholefoodsmarket.com/products")
    category_elements = driver.find_elements(
        by=By.XPATH,
        value="//a[@data-csa-c-slot-id='Category' and not(contains(@href, 'all-products'))]",
    )
    categories_dict = {}
    for element in category_elements:
        category = element.find_element(by=By.XPATH, value=".//span").text
        category_url = element.get_attribute("href")
        categories_dict[category] = category_url
    return categories_dict


def parse_subcategories(driver, category, category_url, csv_writer):
    driver.get(category_url)

    subcategory_elements = driver.find_elements(
        by=By.XPATH,
        value="//nav[@aria-label='category and filter navigation']//li[@data-testid='browse-menu-item-1']",
    )
    for i, _ in enumerate(subcategory_elements):
        subcategory = (
            subcategory_elements[i].find_element(by=By.XPATH, value=".//span").text
        )
        print(subcategory)

        action = ActionChains(driver)
        action.move_to_element(to_element=subcategory_elements[i])
        action.click()
        action.perform()
        time.sleep(2)

        page = load_all_products(driver)
        extract_products(category, subcategory, csv_writer, page)

        back = driver.find_element(
            by=By.XPATH,
            value="(//nav[@aria-label='category and filter navigation']//a[@aria-expanded='true'])[1]",
        )
        click(back, driver)

        subcategory_elements = driver.find_elements(
            by=By.XPATH,
            value="//nav[@aria-label='category and filter navigation']//li[@data-testid='browse-menu-item-1']",
        )


def scrape_wholefoodsmarket(driver, output_csv):

    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = ("name", "brand", "category", "subcategory", "price")
        csv_writer.writerow(headers)

        subcategories_dict = get_categories_dict(driver)
        for category, category_url in subcategories_dict.items():
            parse_subcategories(driver, category, category_url, csv_writer)


if __name__ == "__main__":
    # options = Options()
    # options.add_experimental_option("prefs", {"geolocation": True})
    options = Options()
    # options.add_argument(
    #     r"user-data-dir=/home/atehe/.config/google-chrome/Default"
    # )  # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
    # options.add_argument(r"profile-directory=Profile 1")
    options.add_argument(
        r"user-data-dir=/home/atehe/.config/google-chrome/Default/Profile 1"
    )

    driver = uc.Chrome(version_main=100, options=options)

    # latitude = 42.1408845
    # longitude = -87.5033907
    # accuracy = 100

    # driver.maximize_window()
    # driver.execute_cdp_cmd(
    #     "Emulation.setGeolocationOverride",
    #     {
    #         "latitude": latitude,
    #         "longitude": longitude,
    #         "accuracy": accuracy,
    #     },
    # )

    driver.get(
        "https://www.wholefoodsmarket.com/products/dairy-eggs/cheese?diets=vegan"
    )
    page = load_all_products(driver)
    extract_products("category", "subcategory", "csv_writer", page)
    time.sleep(1000)
