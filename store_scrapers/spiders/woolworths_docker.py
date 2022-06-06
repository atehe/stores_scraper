import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging, time

from store_scrapers.scripts.aldi import click
from selenium.webdriver.common.action_chains import ActionChains


# def click(element, driver):
#     action = ActionChains(driver)
#     action.move_to_element(to_element=element)
#     action.click()
#     action.perform()
#     time.sleep(1)


def get_subcategories(driver):
    """Returns a list of dictionaries containing the category, subcategory and subcategory URL"""

    driver.maximize_window()
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
    logging.info("Getting categories, subcategories and URL...")
    for i, category_elem in enumerate(category_elements):
        category = category_elements[i].text
        click(category_elements[i], driver)
        subcategory_elements = driver.find_elements(
            by=By.XPATH, value="//ul[@class='categoriesNavigation-list']//a"
        )
        for subcategory_elem in subcategory_elements:
            subcategory = subcategory_elem.text
            subcategory_url = subcategory_elem.get_attribute("href")
            logging.info(
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
            category_elements = driver.find_elements(
                by=By.XPATH,
                value="//a[@aria-controls='categoryHeader-menu' and not(contains(text(), 'Specials')) and not(contains(text(), 'Front of Store'))]",
            )
    return subcategories_list


class WoolworthsDockerSpider(scrapy.Spider):
    name = "woolworths_docker"
    allowed_domains = ["www.woolworths.com.au"]
    start_urls = ["http://www.woolworths.com.au/"]

    def start_requests(self):
        yield SeleniumRequest(
            url="http://www.woolworths.com.au/", callback=self.parse_subcategories
        )

    def parse_subcategories(self, response):
        driver = response.meta["driver"]
        subcategories_list = get_subcategories(driver)

        for dict_ in subcategories_list:
            yield dict_
