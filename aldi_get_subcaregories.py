from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, logging

logging.basicConfig(level=logging.INFO)


def excluded_keyword_in(word):
    excluded_tags = [
        "all ",
        " all",
        "offer",
        "about",
        "price",
        "inspired",
        "best of",
    ]
    for tag in excluded_tags:
        if tag in word:
            return True
    return False


def click(element, driver):
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(1.5)


def handle_cookies(driver):
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

    url_list = []
    for category_item in category_items[:-1]:

        category = category_item.find_element(
            by=By.XPATH, value=".//span[@class='linkName ']"
        ).text

        click(category_item, driver)
        logging.info(f"Getting subcategories for {category.title()}")

        subcategory_groups = driver.find_elements(
            by=By.XPATH,
            value="//ul[@class='header__list header__list--secondary js-list js-second-level-submenu expanded']/li[@class='header__item header__item--secondary single-fourth js-list-toggle js-list-dropdown avoid-click-lg']",
        )
        for subcategory_group in subcategory_groups:
            group_name = subcategory_group.find_element(
                by=By.XPATH, value="./div/a"
            ).text

            if excluded_keyword_in(group_name.lower()):
                continue

            subcategories = subcategory_group.find_elements(
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

                if excluded_keyword_in(subcategory.lower()):
                    continue

                url_list.append(
                    {
                        "category": category,
                        "subcategory_group": group_name,
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


if __name__ == "__main__":
    driver = webdriver.Chrome()

    subcategories_url = get_subcategories(driver)
    print(subcategories_url)
    print(len(subcategories_url))
