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


driver = uc.Chrome(version_main=100)
driver.get("https://www.loblaws.ca/")

hamburger_button = WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable((By.XPATH, "//button[@class='mobile-menu__button']"))
)
# click(hamburger, driver)

print("hello")
category_elements = driver.find_elements(
    by=By.XPATH,
    value="//li[@class='primary-nav__list__item primary-nav__list__item--with-children']",
)
print(category_elements)

for category_element in category_elements:
    print("hello")
    category = category_element.find_element(by=By.XPATH, value="./button/span").text
    subcategory_elements = category_element.find_elements(by=By.XPATH, value="./ul/li")

    for subcategory_element in subcategory_elements:
        subcategory = subcategory_element.find_element(
            by=By.XPATH, value="./a/span"
        ).text
        subcategory_url = subcategory_element.find_element(
            by=By.XPATH, value="./a"
        ).get_attribute("href")

        print(f"{category}|{subcategory}|{subcategory_url}")


# product_response = Selector(text=driver.page_source)
# products = product_response.xpath("//li[@class='product-tile-group__list__item']")

# for product in products:
#     brand = product.xpath("//span[@class='product-name__item product-name__item--brand']//text()").get()
