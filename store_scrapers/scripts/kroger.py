from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, logging
from aldi import click, excluded_keyword_in
from scrapy.selector import Selector
from selenium.webdriver.common.action_chains import ActionChains
import undetected_chromedriver as uc
from csv import writer

logging.basicConfig(level=logging.INFO)


def extract_product_id(url):
    """Returns product id from product url"""
    try:
        last_slash_index = url[::-1].index("/")
        question_mark_index = url[::-1].index("?") + 1
        return url[-last_slash_index:-question_mark_index]
    except:
        return url


def get_subcategories(driver):
    driver.get("https://www.kroger.com/")

    harmburger_menu = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='KrogerHeader-SiteMenu']"))
    )
    click(harmburger_menu, driver)

    category_items = driver.find_elements(
        by=By.XPATH,
        value="//div[contains(text(),'Department')]/following-sibling::div[@class='SiteMenu-SubList pt-8']/button",
    )
    excluded_tags = ["summer", "ways to", "all ", " all", "order "]
    url_list = []
    for i, _ in enumerate(category_items):
        category = category_items[i].text
        if excluded_keyword_in(category):
            continue

        click(category_items[i], driver)

        subcategory_items = driver.find_elements(
            by=By.XPATH,
            value="//a[contains(@class,'kds-Link kds-Link--l kds-Link--implied SiteMenu-Link')]",
        )
        for subcategory_item in subcategory_items:
            subcategory = subcategory_item.text
            subcategory_url = subcategory_item.get_attribute("href")
            if excluded_keyword_in(subcategory, excluded_tags):
                continue
            url_list.append(
                {
                    "category": category,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )

            print(subcategory, subcategory_url)

        back_button = driver.find_element(
            by=By.XPATH, value="//button[@data-testid='SiteMenuBackToMainMenuButton']"
        )
        click(back_button, driver)

        category_items = driver.find_elements(
            by=By.XPATH,
            value="//div[contains(text(),'Department')]/following-sibling::div[@class='SiteMenu-SubList pt-8']/button",
        )
    print(url_list)
    return url_list


def extract_products(driver, csv_writer, subcategory, category):
    page_num = 1

    while True:
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//div[@class='AutoGrid-cell min-w-0']")
            )
        )

        page_response = Selector(text=driver.page_source.encode("utf8"))

        products = page_response.xpath("//div[@class='AutoGrid-cell min-w-0']")

        for product in products:
            name = product.xpath(
                ".//h3[@data-qa='cart-page-item-description']/text()"
            ).get()
            url = product.xpath(
                ".//a[contains(@class,'ProductDescription-truncated')]/@href"
            ).get()
            if not url.startswith("http"):
                url = f"https://www.kroger.com{url}"

            price = product.xpath(".//data[@typeof='Price']/@value").get()
            product_id = extract_product_id(url)
            csv_writer.writerow(
                (
                    name,
                    subcategory,
                    category,
                    product_id,
                    url,
                    price,
                )
            )
            print(
                (
                    name,
                    subcategory,
                    category,
                    product_id,
                    url,
                    price,
                )
            )

        # pagination
        try:
            next_page = driver.find_element(
                by=By.XPATH, value="//button[@aria-label='Next page']"
            )
            logging.info(f"Moving to page {page_num} in {category}")
            action = ActionChains(driver)
            action.move_to_element(to_element=next_page)
            action.click()
            action.perform()
            continue
        except:
            break


def scrape_kroger(driver, subcategories_dict, output_csv):
    with open(output_csv, "a") as csv_file:
        csv_writer = writer(output_csv)
        headers = ("name", "subcategory", "category", "product_id", "url", "price")
        csv_writer.writerow(headers)


if __name__ == "__main__":
    # driver = webdriver.Chrome()
    driver = uc.Chrome(version_main=100)
    driver.maximize_window()

    driver.get("https://www.kroger.com/pl/snacks/1801200001")
    extract_products(driver)
    # print

    shop_all = "//a[contains(@class, 'ProminentLink') and not (contains(@href, '?'))]"
