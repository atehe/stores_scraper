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
from selenium.webdriver.chrome.service import Service


def extract_product_id(url):
    last_slash_index = url[::-1].index("/")
    return url[-last_slash_index:]


driver = uc.Chrome(version_main=100)


def get_subcategories(driver):
    driver.get("https://www.loblaws.ca/")
    WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, "//nav[@class='primary-nav']"))
    )

    page_response = Selector(text=driver.page_source)

    categories = page_response.xpath(
        "//li[@class='primary-nav__list__item primary-nav__list__item--with-children']"
    )
    subcategories_list = []
    for category in categories:
        category_name = category.xpath("./button/span//text()").get()

        subcategories = category.xpath("./ul/li")
        for subcategory in subcategories:
            subcategory_name = subcategory.xpath("./a/span//text()").get()
            subcategory_url = subcategory.xpath("./a/@href").get()

            subcategories_list.append(
                {
                    "category": category,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )
    return subcategories_list


def extract_products(driver, url):
    driver.get(url)
    WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//li[@class='product-tile-group__list__item']")
        )
    )

    product_response = Selector(text=driver.page_source)
    products = product_response.xpath("//li[@class='product-tile-group__list__item']")

    for product in products:

        brand = product.xpath(
            ".//span[@class='product-name__item product-name__item--brand']//text()"
        ).get()
        name = product.xpath(
            ".//span[@class='product-name__item product-name__item--name']//text()"
        ).get()
        price = "".join(
            product.xpath(".//div[@class='selling-price-list__item']//text()").getall()
        )
        product_url = product.xpath(
            ".//a[@class='product-tile__details__info__name__link']/@href"
        ).get()
        if not product_url.startswith("http"):
            product_url = f"https://www.loblaws.ca{product_url}"
        product_id = extract_product_id(product_url)

        print(brand, name, price, product_url, product_id)

    # loadmore = //button[@class='primary-button primary-button--load-more-button']


extract_products(
    driver,
    "https://www.loblaws.ca/food/fruits-vegetables/c/28000?navid=flyout-L2-fruits-vegetables",
)
