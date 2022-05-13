from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def excluded_keyword_in(keyword):
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
        if tag in keyword:
            return True
    return False


def click(element, driver):
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(1.5)


driver = webdriver.Chrome()

driver.get("https://www.aldi.co.uk/")
wait = WebDriverWait(driver, 30)


cookies = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, '//button[@id="onetrust-accept-btn-handler"]')
    )
)
cookies.click()

harmburger_menu = wait.until(
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
    print(category.upper())

    click(category_item, driver)

    category_groups = driver.find_elements(
        by=By.XPATH,
        value="//ul[@class='header__list header__list--secondary js-list js-second-level-submenu expanded']/li[@class='header__item header__item--secondary single-fourth js-list-toggle js-list-dropdown avoid-click-lg']",
    )
    for category_group in category_groups:
        group_name = category_group.find_element(by=By.XPATH, value="./div/a").text

        if excluded_keyword_in(group_name.lower()):
            continue
        print(group_name.upper())

        subcategories = category_group.find_elements(by=By.XPATH, value="./ul//li")
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
            print(subcategory)
            url_list.append(
                {
                    "category": category,
                    "category_group": group_name,
                    "subcategory": subcategory,
                    "subcategory_url": subcategory_url,
                }
            )

    back_button = driver.find_element(
        by=By.XPATH, value="//div[@class='back_container js-menu-back']"
    )
    click(back_button, driver)

print(url_list)
