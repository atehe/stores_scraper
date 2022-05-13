from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, logging
from aldi_get_subcaregories import click

logging.basicConfig(level=logging.INFO)


def excluded_keyword_in(word):
    excluded_tags = ["summer", "ways to", "all ", " all", "order "]
    for tag in excluded_tags:
        if tag in word.lower():
            return True
    return False


driver = webdriver.Chrome()

driver.get("https://www.kroger.com/")

harmburger_menu = WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.XPATH, "//div[@class='KrogerHeader-SiteMenu']"))
)
print("harmburger")
click(harmburger_menu, driver)

category_items = driver.find_elements(
    by=By.XPATH,
    value="//div[contains(text(),'Department')]/following-sibling::div[@class='SiteMenu-SubList pt-8']/button",
)
url_list = []
for i, category_item in enumerate(category_items):
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
        if excluded_keyword_in(subcategory):
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
    # time.sleep(5)
    category_items = driver.find_elements(
        by=By.XPATH,
        value="//div[contains(text(),'Department')]/following-sibling::div[@class='SiteMenu-SubList pt-8']/button",
    )
print(url_list)
