from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def clean_category_name(category):
    return category.strip("Shop").strip("department").strip("aisle").strip("\n")


driver = webdriver.Chrome()
driver.get("https://www.tesco.com/groceries/en-GB/")
wait = WebDriverWait(driver, 10)

subcategory_list = []
categories_element = driver.find_elements(
    by=By.XPATH, value="//li[contains(@class,'menu__item--superdepartment')]"
)
print(categories_element)
for category_element in categories_element[:-1]:
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, ".//li[contains(@class,'menu__item--superdepartment')]")
        )
    )
    try:
        category_element.click()
    except:
        driver.execute_script("arguments[0].click();", category_element)

    category = category_element.find_element(by=By.XPATH, value="./a/span").text
    category = clean_category_name(category)

    print(category)

    time.sleep(2)

    subcategories_element = category_element.find_elements(
        by=By.XPATH, value=".//li[contains(@class, 'menu__item--department')]"
    )
    print(len(subcategories_element))
    for subcategory_element in subcategories_element[1:]:
        subcategory = subcategory_element.find_element(
            by=By.XPATH, value="./a/span"
        ).text
        subcategory = clean_category_name(subcategory)
        subcategory_url = subcategory_element.find_element(
            by=By.XPATH, value="./a"
        ).get_attribute("href")
        print(subcategory, subcategory_url)
        subcategory_list.append(
            {
                "category": category,
                "subcategory": subcategory,
                "subcategory_url": subcategory_url,
            }
        )


print(subcategory_list)

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
