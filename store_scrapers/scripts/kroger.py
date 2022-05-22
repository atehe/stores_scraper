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

logging.basicConfig(level=logging.INFO)


SUBCATEGORIES_LIST = "./utils/kroger/subcatecories_url.json"  # list of dictionaries containing category, subcategory and subcategory URL
EXTRACTED_SUBCATEGORIES = "./utils/kroger/extracted_subcategories.json"  # contains list of subcategories extracted, used to resume  scraping when blocked
EXTRACTED_URLS = "./utils/kroger/extracted_url.txt"  # contains urls of pages extracted in each subcategory, used to resume from exact page number when blocked


def page_num_in_url(url):
    try:
        num_start_index = url.index("=") + 1
        return int(url[num_start_index:])
    except:
        return 1


def get_last_extracted_url(extracted_urls, base_url):
    """git sReturns the last extracted page url of a base url(subcategory)"""
    try:
        contains_base_url = [url for url in extracted_urls if url.startswith(base_url)]
        last_extracted_url = max(contains_base_url, key=page_num_in_url)
        return last_extracted_url
    except:
        return base_url


def extract_product_id(url):
    """Returns product id from product url"""
    try:
        last_slash_index = url[::-1].index("/")
        question_mark_index = url[::-1].index("?") + 1
        return url[-last_slash_index:-question_mark_index]
    except:
        return url


def handle_coupons_popup(driver):
    try:
        popup = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[@class='kds-Button kds-Button--secondary kds-Modal-actionButton kds-Modal-actionButton--secondary']",
                )
            )
        )
        click(popup, driver)
    except:
        print("pop up handled")


def get_subcategories(driver):
    """
    Returns a list of dictionaries containing the
    category, subcategory, and subcategory_url of products
    while navigating through the harmburger menu
    """

    # read and return past extracted subcategories
    if os.path.exists(SUBCATEGORIES_LIST):
        with open(SUBCATEGORIES_LIST) as url_list:
            return json.load(url_list)

    driver.get("https://www.kroger.com/")
    handle_coupons_popup(driver)

    harmburger_menu = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='KrogerHeader-SiteMenu']"))
    )
    click(harmburger_menu, driver)

    category_items = driver.find_elements(
        by=By.XPATH,
        value="//div[contains(text(),'Department')]/following-sibling::div[@class='SiteMenu-SubList pt-8']/button",
    )

    excluded_tags = [
        "summer",
        "ways to",
        "all ",
        " all",
        "order ",
    ]  # prevents major category/promational subcategory to be added as subcategory url
    url_list = []
    for i, _ in enumerate(category_items):
        category = category_items[i].text
        if excluded_keyword_in(category, excluded_tags):
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
            logging.info(f"{subcategory}: {subcategory_url}")
            url_list.append(
                {
                    "category": category,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )
        back_button = driver.find_element(
            by=By.XPATH, value="//button[@data-testid='SiteMenuBackToMainMenuButton']"
        )
        click(back_button, driver)

        category_items = driver.find_elements(
            by=By.XPATH,
            value="//div[contains(text(),'Department')]/following-sibling::div[@class='SiteMenu-SubList pt-8']/button",
        )

    # save url_list for next time
    with open(SUBCATEGORIES_LIST, "w") as json_file:
        json.dump(url_list, json_file)
    return url_list


def extract_products(
    driver,
    csv_writer,
    category,
    subcategory,
    log_object,
):
    """Write all products in a subcategory with a csv_writer to file"""

    page_num = page_num_in_url(driver.current_url)
    while True:
        try:
            search_text = driver.find_element(
                by=By.XPATH, value="//div[@class='SearchMessage']//span"
            ).text
            if "There were no results" in search_text:
                break
        except:
            pass

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//nav[@aria-label='Pagination']")
                )
            )
        except:
            try:
                # navigate to product page
                shop_all_url = driver.find_element(
                    by=By.XPATH,
                    value="//a[contains(@class, 'ProminentLink') and not (contains(@href, '?'))]",
                )
                click(shop_all_url, driver)
                continue
            except:
                # quit scraper if access denied
                if "Access Denied" in driver.page_source:
                    logging.critical("ACCESS DENIED!!! Run scraper again to resume...")
                    driver.close()
                    sys.exit()

                else:
                    # refresh page if products doesn't load
                    driver.refresh()
                continue

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
        log_object.write(f"{driver.current_url}\n")  # add url to extracted urls

        # pagination
        try:
            next_page = driver.find_element(
                by=By.XPATH,
                value="//button[@aria-label='Next page' and not(@disabled)]",
            )
            action = ActionChains(driver)
            action.move_to_element(to_element=next_page)
            action.click()
            action.perform()

            page_num += 1
            logging.info(f"Moving to page {page_num} in {subcategory}")
            continue
        except:
            break
    logging.info(f"EXTRACTION COMPLETE FOR {subcategory.upper()}")

    # save extracted subcategories
    with open(EXTRACTED_SUBCATEGORIES) as extracted:
        extracted_subcategories = json.load(extracted)

    extracted_subcategories.append(subcategory)
    with open(EXTRACTED_SUBCATEGORIES, "w") as extracted:
        json.dump(extracted_subcategories, extracted)


def scrape_kroger(driver, subcategories_list, output_csv):
    """Extracts all products from kroger and store in csv"""

    # read past extracted subcategories
    if os.path.exists(EXTRACTED_SUBCATEGORIES):
        with open(EXTRACTED_SUBCATEGORIES) as extracted:
            extracted_subcategories = json.load(extracted)
    else:
        extracted_subcategories = []
        with open(EXTRACTED_SUBCATEGORIES, "w") as extracted:
            json.dump(extracted_subcategories, extracted)

    # read past extracted pages/url
    if not os.path.exists(EXTRACTED_URLS):
        with open(EXTRACTED_URLS, "w") as log_object:
            extracted_urls = []
    else:
        with open(EXTRACTED_URLS, "r") as log_object:
            extracted_urls = log_object.read().splitlines()

    # Open csv and log file for extracted products and extracted url/page to be written to
    with open(output_csv, "a") as csv_file, open(EXTRACTED_URLS, "a") as log_object:
        csv_writer = writer(csv_file)
        headers = ("name", "subcategory", "category", "product_id", "url", "price")
        csv_writer.writerow(headers)

        for subcategory_dict in subcategories_list:
            category = subcategory_dict["category"]
            subcategory = subcategory_dict["subcategory"]
            subcategory_url = subcategory_dict["subcategory_url"]

            if subcategory in extracted_subcategories:
                continue

            resume_url = get_last_extracted_url(extracted_urls, subcategory_url)

            driver.get(resume_url)

            extract_products(
                driver,
                csv_writer,
                category,
                subcategory,
                log_object,
            )


if __name__ == "__main__":
    # random useragents to use with chrome
    ua = UserAgent()
    OPTS = Options()
    OPTS.add_argument(f"user-agent={ua.random}")

    driver = uc.Chrome(version_main=100, options=OPTS)
    if not os.path.exists("./utils/kroger"):  # folder to store script files
        os.mkdir("./utils/kroger")

    subcategories = get_subcategories(driver)

    driver.maximize_window()
    scrape_kroger(
        driver,
        subcategories,
        "kroger_products_trial.csv",
    )
