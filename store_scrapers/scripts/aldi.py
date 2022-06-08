from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector
from csv import writer
import time, logging, sys

logging.basicConfig(level=logging.INFO)
DRIVER_EXECUTABLE_PATH = "./utils/chromedriver"


def excluded_keyword_in(word, excluded_tags):
    """Returns True if  an excluded keyword is in word"""
    for tag in excluded_tags:
        if tag.lower() in word.lower():
            return True
    return False


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(1.5)


def handle_cookies(driver):
    """Accepts cookies if dialog pops up"""
    try:
        cookies = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
            )
        )
        cookies.click()
        logging.info("Cookies Accepted")
    except:
        logging.info("Cookies popup not found")


def get_subcategories(driver):
    """Returns list of dictionaries containing subcategory url, subcategory, shopping group and category"""

    driver.get("https://www.aldi.co.uk/")

    handle_cookies(driver)

    harmburger_menu = WebDriverWait(driver, 30).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[@class='sr-only' and contains(text(), 'Aldi Menu')]")
        )
    )
    click(harmburger_menu, driver)

    category_items = driver.find_elements(
        by=By.XPATH,
        value="//li[@class='header__item header__item--nav slim-fit js-list-toggle text-uppercase']",
    )

    # tags of full categories or ads categories(needed are subcategories)
    excluded_tags = [
        "all ",
        " all",
        "offer",
        "about",
        "price",
        "inspired",
        "best of",
    ]

    url_list = []
    for category_item in category_items[:-1]:

        category = category_item.find_element(
            by=By.XPATH, value=".//span[@class='linkName ']"
        ).text

        click(category_item, driver)
        logging.info(f"Getting subcategories for {category.title()}")

        category_shopping_groups = driver.find_elements(
            by=By.XPATH,
            value="//ul[@class='header__list header__list--secondary js-list js-second-level-submenu expanded']/li[@class='header__item header__item--secondary single-fourth js-list-toggle js-list-dropdown avoid-click-lg']",
        )
        for category_shopping_group in category_shopping_groups:
            group_name = category_shopping_group.find_element(
                by=By.XPATH, value="./div/a"
            ).text

            if excluded_keyword_in(group_name, excluded_tags):
                continue

            subcategories = category_shopping_group.find_elements(
                by=By.XPATH, value="./ul//li"
            )
            for subcategory_elem in subcategories:
                try:
                    subcategory = subcategory_elem.find_element(
                        by=By.XPATH, value=".//a"
                    ).text
                    subcategory_url = subcategory_elem.find_element(
                        by=By.XPATH, value=".//a"
                    ).get_attribute("href")
                except:
                    continue

                if excluded_keyword_in(subcategory, excluded_tags):
                    continue

                logging.debug(
                    {
                        "category": category,
                        "category_shopping_group": group_name,
                        "subcategory": subcategory,
                        "subcategory_url": subcategory_url,
                    }
                )

                url_list.append(
                    {
                        "category": category,
                        "category_shopping_group": group_name,
                        "subcategory": subcategory,
                        "subcategory_url": subcategory_url,
                    }
                )

        back_button = driver.find_element(
            by=By.XPATH, value="//div[@class='back_container js-menu-back']"
        )
        click(back_button, driver)
    return url_list


def load_all_products(url, driver):
    """Pagination by clicking load more button till page is fully loaded"""
    driver.maximize_window()
    driver.get(url)

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

    logging.debug(">>> page loading complete")
    return driver.page_source


def extract_product_id(url):
    """Returns product id from product url"""
    try:
        last_slash_index = url[::-1].index("/")
        return url[-last_slash_index:]
    except:
        return url


def extract_details(page, csv_writer, category, subcategory, category_shopping_group):
    """writes extracted products to an open csv file writer"""

    page_response = Selector(text=page.encode("utf8"))

    products = page_response.xpath("//div[contains(@class,'hover-item')]")
    if products:
        logging.info(f">>> Scraping {subcategory} in {category}...")
    for product in products:
        url = product.xpath(".//a[@class='category-item__link']/@href").get()
        if not url.startswith("http"):
            url = f"https://www.aldi.co.uk{url}"

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

        rating = product.xpath(".//a[@itemprop='aggregateRating']/@aria-label").get()
        product_id = extract_product_id(url)

        logging.debug(
            f">>> {name}, {category.title()}, {subcategory}, {category_shopping_group}, {product_id}, {url}, {price}, {rating}"
        )

        csv_writer.writerow(
            (
                name,
                category.title(),
                subcategory,
                category_shopping_group,
                product_id,
                url,
                price,
                rating,
            )
        )


def scrape_aldi(driver, subcategories_url, output_csv):

    with open(output_csv, "a") as csv_file:
        csv_writer = writer(csv_file)
        headers = (
            "Name",
            "Category",
            "Subcategory",
            "Category Shopping Group",
            "Product ID",
            "Product URL",
            "Price",
            "Rating",
        )
        if os.stat(output_csv).st_size == 0:
            csv_writer.writerow(headers)

        for subcategory_dict in subcategories_url:
            category = subcategory_dict["category"]
            category_shopping_group = subcategory_dict["category_shopping_group"]
            subcategory = subcategory_dict["subcategory"]
            subcategory_url = subcategory_dict["subcategory_url"]

            product_page = load_all_products(subcategory_url, driver)

            extract_details(
                product_page, csv_writer, category, subcategory, category_shopping_group
            )


if __name__ == "__main__":

    output_csv = sys.argv[-1]

    service = Service(DRIVER_EXECUTABLE_PATH)
    driver = webdriver.Chrome(
        service=service,
    )
    subcategories_url = get_subcategories(driver)

    scrape_aldi(driver, subcategories_url, output_csv)
