import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.utils.response import open_in_browser
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from store_scrapers.spiders.tesco import extract_product_id


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


class AldiSpider(scrapy.Spider):
    name = "aldi"
    allowed_domains = ["aldi.co.uk"]

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.aldi.co.uk/",
            callback=self.parse_subcategories_url,
        )

    def parse_subcategories_url(self, response):
        # open_in_browser(response)
        driver = response.meta["driver"]
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
                print(group_name.upper())

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
                    print(subcategory)
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

        for url_dict in url_list[:5]:
            category = url_dict["category"]
            subcategory_group = url_dict["subcategory_group"]
            subcategory = url_dict["subcategory"]
            subcategory_url = url_dict["subcategory_url"]
            yield SeleniumRequest(
                url=subcategory_url,
                callback=self.parse_products,
                meta={
                    "category": category,
                    "subcategory_group": group_name,
                    "subcategory": subcategory,
                },
                wait_time=5,
                # wait_until=EC.element_to_be_clickable(
                #     (By.CLASS_NAME, "category-item__wrapper-link js-product-link")
                # ),
                script="window.scrollTo(0, document.body.scrollHeight);",
            )

    def parse_products(self, response):
        open_in_browser(response)
        category = response.meta["category"]
        subcategory_group = response.meta["subcategory_group"]
        subcategory = response.meta["subcategory"]

        products = response.xpath(
            "//div[contains(@class,'hover-item category-item js-category-item')]"
        )

        for product in products:
            url = product.xpath(".//a[@class='category-item__link']/@href").get()
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

            rating = product.xpath(
                ".//a[@itemprop='aggregateRating']/@aria-label"
            ).get()
            product_id = extract_product_id(url)

            yield {
                "Name": name,
                "Category": category.title(),
                "Subcategory": subcategory,
                "Subcategory Group": subcategory_group,
                "Product ID": product_id,
                "Product URL": url,
                "Price": price,
                "Rating": rating,
            }
