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
import time, logging, random, json, os

logging.basicConfig(level=logging.INFO)


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

    # load list from previous extraction
    if os.path.exists("./utils/kroger/subcatecories_url.json"):
        with open("./utils/kroger/subcatecories_url.json") as url_list:
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
    ]  # prevents category/promational subcategory to be added to list
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
    with open("./utils/kroger/subcatecories_url.json", "w") as json_file:
        json.dump(url_list, json_file)
    return url_list


def extract_products(driver, csv_writer, category, subcategory):
    """Write all products in a subcategory with a csv_writer to file"""

    page_num = 1
    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@class='AutoGrid-cell min-w-0']")
                )
            )
        except:
            try:
                # move to product page
                shop_all_url = driver.find_element(
                    by=By.XPATH,
                    value="//a[contains(@class, 'ProminentLink') and not (contains(@href, '?'))]",
                )
                click(shop_all_url, driver)
                continue
            except:
                # restart chrome when blocked
                if "Access Denied" in driver.page_source:
                    last_url = driver.current_url()
                    driver.quit()

                    time.sleep(random.randint(25, 45))
                    driver.get_last(last_url)
                else:
                    driver.refresh()  # refresh page if products doesn't load
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
            logging.info(
                (
                    name,
                    subcategory,
                    category,
                    product_id,
                    url,
                    price,
                )
            )
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

            logging.info(f"Moving to page {page_num} in {subcategory}")
            page_num += 1
            continue
        except:
            break
    logging.info(f"EXTRACTION COMPLETE FOR {subcategory.upper()}")

    # save extracted subcategory
    with open("./utils/kroger/extracted_subcategories.json") as extracted:
        extracted_subcategories = json.load(extracted)

    extracted_subcategories.append(subcategory)
    with open("./utils/kroger/extracted_subcategories.json") as extracted:
        json.dump(extracted_subcategories, extracted)


def scrape_kroger(driver, subcategories_list, output_csv):
    """Extract all products from kroger and store in csv"""

    if os.path.exists("./utils/kroger/extracted_subcategories.json"):
        with open("./utils/kroger/extracted_subcategories.json") as extracted:
            extracted_subcategories = json.load(extracted)
    else:
        extracted_subcategories = []
        with open("./utils/kroger/extracted_subcategories.json", "w") as extracted:
            json.dump(extracted_subcategories, extracted)

    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = ("name", "subcategory", "category", "product_id", "url", "price")
        csv_writer.writerow(headers)

        for subcategory_dict in subcategories_list:
            category = subcategory_dict["category"]
            subcategory = subcategory_dict["subcategory"]
            subcategory_url = subcategory_dict["subcategory_url"]

            if subcategory in extracted_subcategories:
                continue
            driver.get(subcategory_url)
            extract_products(driver, csv_writer, category, subcategory)


if __name__ == "__main__":
    # random useragents to use with chrome
    ua = UserAgent()
    opts = Options()
    opts.add_argument(f"user-agent={ua.random}")

    driver = uc.Chrome(version_main=100, options=opts)
    if not os.path.exists("./utils/kroger"):  # folder to store script files
        os.mkdir("./utils/kroger")

    subcategories = get_subcategories(driver)

    driver.maximize_window()
    scrape_kroger(driver, subcategories, "kroger_products_trial.csv")
