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
import random


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
from scrapy.selector import Selector
from csv import writer

driver = uc.Chrome(version_main=100)
driver.maximize_window()
# driver.get("https://www.walmart.com/all-departments")
driver.get(
    "https://www.walmart.com/browse/home-improvement/dehumidifiers/1072864_133032_1231459_112918?povid=HardlinesGlobalNav_DSK_HomeImprovement_AirQualityWaterPurification_Dehumidifiers&affinityOverride=default"
)
time.sleep(random.randint(2, 4))

with open("walmart.csv", "a") as csv_file:
    csv_writer = writer(csv_file)

    page_response = Selector(text=driver.page_source.encode("utf8"))
    items = []

    num_pages = page_response.xpath(
        "//nav[@aria-label='pagination']//li[last()-1]//text()"
    ).get()
    num_pages = int(num_pages)
    print(num_pages)
    page = 2
    while page <= num_pages:
        page_response = Selector(text=driver.page_source.encode("utf8"))
        products = page_response.xpath(
            "//div[@class='mb1 ph1 pa0-xl bb b--near-white w-25']"
        )
        for product in products:
            id = product.xpath("./div/div/@data-item-id").get()
            url = product.xpath("./div/div/a/@href").get()
            name = product.xpath("./div/div/a//text()").get()
            price = product.xpath("./div/div/div/div[2]/div[1]//text()").get()
            rating = product.xpath("./div/div/div/div[2]/div[2]/span[3]//text()").get()
            print((name, id, url, price, rating))
            csv_writer.writerow((name, id, url, price, rating))
            # try:
            #     next_page = driver.find_element(
            #         by=By.XPATH, value="//a[@aria-label='Next Page']"
            #     )
            #     action = ActionChains(driver)
            #     action.move_to_element(to_element=next_page)
            #     action.click()
            #     action.perform()
            # except:
            #     break
        driver.get(
            f"https://www.walmart.com/browse/home-improvement/dehumidifiers/1072864_133032_1231459_112918?povid=HardlinesGlobalNav_DSK_HomeImprovement_AirQualityWaterPurification_Dehumidifiers&affinityOverride=default&page={page}"
        )
        page += 1


# department_button = WebDriverWait(driver, 30).until(
#     EC.presence_of_element_located((By.XPATH, "//a[@link-identifier='Departments']"))
# )
# click(department_button, driver)

# sections = driver.find_elements(
#     by=By.XPATH, value='//div[@class="w_Cf w_De w_Cr w_Cx w_C7 tl mt4"]'
# )

# for section in sections:
#     category = section.find_element(by=By.XPATH, value=".//h2/a").text
#     print(category)
#     subcategory_elements = section.find_elements(by=By.XPATH, value=".//ul/li/a")
#     for subcategory_element in subcategory_elements:
#         subcategory = subcategory_element.text
#         subcategory_url = subcategory_element.get_attribute("href")
#         print(subcategory, subcategory_url)
