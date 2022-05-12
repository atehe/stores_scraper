from gc import callbacks
import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.utils.response import open_in_browser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging


def extract_product_id(url):
    try:
        last_slash_index = url[::-1].index("/")
        return url[-last_slash_index:]
    except:
        return url


def clean_category_name(category):
    return category.strip("Shop").strip("department").strip("aisle").strip("\n")


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["www.tesco.com"]

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.tesco.com/groceries/en-GB/",
            callback=self.parse_subcategory_url,
        )

    def parse_subcategory_url(self, response):
        driver = response.meta["driver"]
        wait = WebDriverWait(driver, 10)

        subcategory_list = []
        categories_element = driver.find_elements(
            by=By.XPATH, value="//li[contains(@class,'menu__item--superdepartment')]"
        )
        for category_element in categories_element[:-1]:
            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, ".//li[contains(@class,'menu__item--superdepartment')]")
                )
            )
            try:
                category_element.click()
            except:
                driver.execute_script("arguments[0].click();", category_element)

            category = category_element.find_element(by=By.XPATH, value="./a/span").text
            category = clean_category_name(category)

            time.sleep(2)

            subcategories_element = category_element.find_elements(
                by=By.XPATH, value=".//li[contains(@class, 'menu__item--department')]"
            )
            for subcategory_element in subcategories_element[1:]:
                subcategory = subcategory_element.find_element(
                    by=By.XPATH, value="./a/span"
                ).text
                subcategory = clean_category_name(subcategory)
                subcategory_url = subcategory_element.find_element(
                    by=By.XPATH, value="./a"
                ).get_attribute("href")
                subcategory_list.append(
                    {
                        "category": category,
                        "subcategory": subcategory,
                        "subcategory_url": subcategory_url,
                    }
                )

        for subcategory_dict in subcategory_list:
            yield SeleniumRequest(
                url=subcategory_dict["subcategory_url"],
                callback=self.get_products_page_url,
                meta={
                    "category": subcategory_dict["category"],
                    "subcategory": subcategory_dict["subcategory"],
                },
            )

    def get_products_page_url(self, response):
        category = response.meta.get("category")
        subcategory = response.meta.get("subcategory")
        product_page_rel_url = response.xpath(
            "//li[@class ='list-item list-subheader']/a/@href"
        ).get()
        abs_url = f"https://www.tesco.com{product_page_rel_url}"
        yield SeleniumRequest(
            url=abs_url,
            callback=self.parse_products,
            meta={"category": category, "subcategory": subcategory},
        )

    def parse_products(self, response):
        category = response.meta.get("category")
        subcategory = response.meta.get("subcategory")

        products = response.xpath("//li[contains(@class, 'product-list')]")

        for product in products:
            name = product.xpath(".//a[@data-auto='product-tile--title']//text()").get()
            rel_url = product.xpath(
                ".//a[@data-auto='product-tile--title']/@href"
            ).get()
            price = "".join(
                product.xpath(
                    ".//div[contains(@class,'price-per-sellable')]//text()"
                ).getall()
            )
            cup_price = "".join(
                product.xpath(
                    ".//div[@class='price-per-quantity-weight']//text()"
                ).getall()
            )
            product_id = extract_product_id(rel_url)
            abs_url = f"https://www.tesco.com{rel_url}"

            yield {
                "Name": name,
                "Category": category,
                "Subcategory": subcategory,
                "Product ID": product_id,
                "Product URL": abs_url,
                "Price": price,
                "Cup Price": cup_price,
            }
        next_page = response.xpath('//a[@title="Go to results page"]/@href').get()
        if next_page:
            url = f"https://www.tesco.com{next_page}"
            yield SeleniumRequest(
                url=url,
                callback=self.parse_products,
                meta={"category": category, "subcategory": subcategory},
            )
