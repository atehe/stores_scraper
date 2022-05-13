import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.utils.response import open_in_browser


class AldiSpider(scrapy.Spider):
    name = "aldi"
    allowed_domains = ["aldi.co.uk"]

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.aldi.co.uk/c/specialbuys/health-and-beauty/medicine",
            callback=self.parse,
        )

    def parse(self, response):
        open_in_browser(response)
