from dataclasses import field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, logging
from scrapy.selector import Selector
from csv import DictWriter

from aldi_get_subcaregories import click, handle_cookies

driver = webdriver.Chrome()


def extract_product_id(url):
    try:
        last_slash_index = url[::-1].index("/")
        return url[-last_slash_index:]
    except:
        return url


def load_all_products(url, driver):
    driver.get(url)
    handle_cookies(driver)

    while True:
        try:
            load_more = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@class='category-loadmore-cta']")
                )
            )
            click(load_more, driver)
        except:
            break

    print("Loading complete")
    return driver.page_source


product_page = load_all_products(
    "https://www.aldi.co.uk/c/specialbuys/garden-shop?q=%3Apopular&page=0&firstPlacementTotalCount=138&secondPlacementTotalCount=36&privm=false",
    driver,
)


def extract_details(page, output_csv):
    with open(output_csv, "a") as csv_file:
        dict_writer = DictWriter(
            csv_file,
            fieldnames=(
                "Name",
                "Category",
                "Subcategory",
                "Subcategory  Group",
                "Product ID",
                "Product URL",
                "Price",
                "Rating",
            ),
        )

        page_response = Selector(text=page.encode("utf8"))

        products = page_response.xpath(
            "//div[contains(@class,'hover-item category-item js-category-item')]"
        )

        for product in products:
            url = product.xpath(".//a[@class='category-item__link']/@href").get()
            name = product.xpath(
                ".//li[contains(@class,'category-item__title')]/text()"
            ).get()
            price = " ".join(
                [
                    word.strip("\n").strip().strip("\n").strip()
                    for word in product.xpath(
                        ".//li[contains(@class,'category-item__price')]/text()"
                    ).getall()
                ]
            )

            rating = product.xpath(
                ".//a[@itemprop='aggregateRating']/@aria-label"
            ).get()
            product_id = extract_product_id(url)

            dict_writer.writerow(
                {
                    "Name": name,
                    # "Category": category.title(),
                    # "Subcategory": subcategory,
                    # "Subcategory Group": subcategory_group,
                    "Product ID": product_id,
                    "Product URL": url,
                    "Price": price,
                    "Rating": rating,
                }
            )

    # ("Name", "Category","Subcategory","Subcategory  Group","Product ID","Product URL","Price","Rating")


extract_details(
    product_page,
    "hello.csv",
)
