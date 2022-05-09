from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
import logging
from selenium import webdriver
import json
from selenium.webdriver.chrome.options import Options
import time
import csv


def get_categories(driver):
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
    for element in category_elements:
        url = element.get_attribute("href")
        category = element.text
        category_dict[category] = url
    return category_dict


def extract_product_id(url):
    try:
        start_index = url.index("productdetails/") + 15
        end_index = url[start_index:].index("/")
        return url[start_index : start_index + end_index]
    except:
        return url


def extract_products(page):
    page_response = Selector(page)
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

        page_products.append(
            {
                "Name": name,
                "Category": "Dairy, Egg & Fridge",
                "Price": ".".join([str(price_dollar), str(price_cent)]),
                "Cup Price": cup_price,
                "Product_URL": f"http://www.woolworths.com.au{url}",
                "Product_ID": extract_product_id(url),
            }
        )
        return page_products


def parse_category(driver, file):
    page_num = 1
    while True:
        logging.debug(f"Extracting products from page {page_num}")
        try:
            next_page = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[@class='paging-next ng-star-inserted']")
                )
            )
            last_page = False
        except:
            logging.info("LAST PAGE")
            last_page = True

        time.sleep(25)  #  wait for products to load
        # driver.implicitly_wait(25)

        page_products = extract_products(driver.page_source.encode("utf-8"))
        page_num += 1

        if last_page:
            break
        action = ActionChains(driver)
        action.move_to_element(to_element=next_page)
        action.click()
        action.perform()
