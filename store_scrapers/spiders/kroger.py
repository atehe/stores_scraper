import scrapy
import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.utils.response import open_in_browser


class KrogerSpider(scrapy.Spider):
    name = "kroger"

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.kroger.com/pl/shrimp/0501000009",
            callback=self.parse,
            wait_time=10,
        )

    def parse(self, response):
        open_in_browser(response)
