from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
import time


driver = webdriver.Chrome()
driver.get("https://www.tesco.com/groceries/en-GB/")
wait = WebDriverWait(driver, 10)


categories_element = driver.find_elements(
    by=By.XPATH, value="//li[contains(@class,'menu__item--superdepartment')]"
)
print(categories_element)
for category_element in categories_element:
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, ".//li[contains(@class,'menu__item--superdepartment')]")
        )
    )
    try:
        category_element.click()
    except:
        driver.execute_script("arguments[0].click();", category_element)
    time.sleep(1)

    # subcategories_element = category_element.find_elements(
    #     by=By.XPATH, value=".//li[contains(@class, 'menu__item--department')]"
    # )
    # print(subcategories_element)
    # for subcategory_element in subcategories_element[1:]:
    #     wait.until(
    #         EC.element_to_be_clickable(
    #             (
    #                 By.XPATH,
    #                 ".//li[contains(@class, 'menu__item--department')]",
    #             )
    #         )
    #     )
    #     # time.sleep(3)
    #     # wait.until(EC.element_to_be_clickable(By.XPATH, "."))
    #     try:
    #         subcategory_element.click()
    #     except:
    #         driver.execute_script("arguments[0].click();", subcategory_element)
    # categories_element = driver.find_elements(
    #     by=By.XPATH, value="//li[contains(@class,'menu__item--superdepartment')]"
    # )
