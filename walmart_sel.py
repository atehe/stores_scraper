from selenium import webdriver

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from scrapy.selector import Selector
from selenium.webdriver.chrome.service import Service
import logging
import csv
import time


def click(element, driver):
    """Use javascript click if selenium click method fails"""
    try:
        element.click()
    except:
        driver.execute_script("arguments[0].click();", element)
    time.sleep(1.5)


# option = webdriver.ChromeOptions()

# option.add_argument("--disable-blink-features")
# option.add_argument("--disable-blink-features=AutomationControlled")
# option.add_argument("window-size=1280,800")
# option.add_argument(
#     "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
# )
# driver = webdriver.Chrome(options=option)
import undetected_chromedriver as uc

driver = uc.Chrome(version_main=100)
driver.maximize_window()
driver.get("https://www.walmart.com/all-departments")


# department_button = WebDriverWait(driver, 30).until(
#     EC.presence_of_element_located((By.XPATH, "//a[@link-identifier='Departments']"))
# )
# click(department_button, driver)

sections = driver.find_elements(
    by=By.XPATH, value='//div[@class="w_Cf w_De w_Cr w_Cx w_C7 tl mt4"]'
)

for section in sections:
    category = section.find_element(by=By.XPATH, value=".//h2/a").text
    print(category)
    subcategory_elements = section.find_elements(by=By.XPATH, value=".//ul/li/a")
    for subcategory_element in subcategory_elements:
        subcategory = subcategory_element.text
        subcategory_url = subcategory_element.get_attribute("href")
        print(subcategory, subcategory_url)
