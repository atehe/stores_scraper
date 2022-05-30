from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aldi import click, excluded_keyword_in
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
from csv import writer
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import logging, json, os, sys, time, random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from fake_useragent import UserAgent
import undetected_chromedriver as uc


logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


def hover(driver, element):
    action = ActionChains(driver)
    action.move_to_element(to_element=element)
    action.perform()
    time.sleep(0.5)


def extract_product_id(url):
    last_slash_index = url[::-1].index("/")
    return url[-last_slash_index:]


def load_all(driver):
    load_more_click_count = 0
    while True:
        try:
            load_more = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[@class='primary-button primary-button--load-more-button']",
                    )
                )
            )
            click(load_more, driver)
            if load_more_click_count == 19:
                logging.critical("ending scroll...")  # page crashes after 20 clicks
            break
            load_more_click_count += 1
        #
        except:
            break


def parse_nav_dept(driver, dept_data_code, output_list):

    dept = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//button[@data-code='{dept_data_code}']")
        )
    )
    hover(driver, dept)
    category_elements = driver.find_elements(
        by=By.XPATH,
        value=f"//button[@data-code='{dept_data_code}']/parent::li/ul/li",
    )
    for category_elem in category_elements:
        hover(driver, category_elem)
        category = category_elem.find_element(by=By.XPATH, value="./a/span").text

        if category.lower().startswith("seasonal") or category.lower().startswith(
            "market"
        ):
            continue

        subcategory_elements = driver.find_elements(
            by=By.XPATH,
            value=f"//ul[@data-code='{dept_data_code}']//li[(@class='primary-nav__list__item' and not (@style)) or (@class='primary-nav__list__item'  and (following-sibling::li[1][@style='margin-top: 10px; padding-bottom: 0px;']) and (@style='margin-top: 10px; padding-bottom: 0px;'))]",
        )
        for subcategory_elem in subcategory_elements:
            subcategory = subcategory_elem.find_element(
                by=By.XPATH, value="./a/span"
            ).text
            subcategory_url = subcategory_elem.find_element(
                by=By.XPATH, value="./a"
            ).get_attribute("href")

            output_list.append(
                {
                    "category": category,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )


def get_subcategories(driver):
    driver.maximize_window()
    driver.get("https://www.loblaws.ca/")
    WebDriverWait(driver, 120).until(
        EC.element_to_be_clickable(
            (By.XPATH, f"//button[@data-code='xp-455-food-departments']")
        )
    )
    subcategories_list = []
    parse_nav_dept(driver, "xp-455-food-departments", subcategories_list)
    parse_nav_dept(driver, "xp-455-nonfood-departments", subcategories_list)

    return subcategories_list


def extract_products(driver, category, subcategory, subcategory_url, csv_writer):
    driver.get(subcategory_url)
    try:
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//li[@class='product-tile-group__list__item']")
            )
        )
    except:
        logging.critical(
            f"{category}: {subcategory} not loaded\nURL: {subcategory_url}"
        )
    load_all(driver)

    try:
        product_response = Selector(text=driver.page_source.encode("utf8"))
        products = product_response.xpath(
            "//li[@class='product-tile-group__list__item']"
        )
    except:
        with open("log.csv", "a") as logfile:
            log_writer = writer(logfile)
            log_writer.writerow((category, subcategory, subcategory_url))

        products = []

        #  restart driver if page crashes
        # driver.quit()
        # driver = None
        # logging.critical("restarting driver...")
        # driver = webdriver.Chrome(
        #     service=service,
        # )

    for product in products:

        brand = product.xpath(
            ".//span[@class='product-name__item product-name__item--brand']//text()"
        ).get()
        name = product.xpath(
            ".//span[@class='product-name__item product-name__item--name']//text()"
        ).get()
        price = " ".join(
            product.xpath(".//div[@class='selling-price-list__item']//text()").getall()
        )
        product_url = product.xpath(
            ".//a[@class='product-tile__details__info__name__link']/@href"
        ).get()
        if not product_url.startswith("http"):
            product_url = f"https://www.loblaws.ca{product_url}"
        product_id = extract_product_id(product_url)

        csv_writer.writerow(
            (name, brand, category, subcategory, product_url, product_id)
        )
    logging.info(f"Extracted {category}: {subcategory}")


def scrape_loblaws(driver, output_csv):
    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = (
            "name",
            "brand",
            "category",
            "subcategory",
            "product url",
            "product_id",
        )
        csv_writer.writerow(headers)

        output_list = get_subcategories(driver)

        for subcategories_dict in output_list[177:]:
            category = subcategories_dict["category"]
            subcategory = subcategories_dict["subcategory"]
            subcategory_url = subcategories_dict["subcategory_url"]
            extract_products(driver, category, subcategory, subcategory_url, csv_writer)


if __name__ == "__main__":

    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(
        service=service,
    )
    # ua = UserAgent()
    # OPTS = Options()
    # OPTS.add_argument(f"user-agent={ua.random}")
    # driver = uc.Chrome(version_main=100, options=OPTS)

    scrape_loblaws(driver, "loblaws_products.csv")
