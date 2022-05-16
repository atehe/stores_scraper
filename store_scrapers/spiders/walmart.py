import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.utils.response import open_in_browser


class WalmartSpider(scrapy.Spider):
    name = "walmart"
    # allowed_domains = ['.']
    # start_urls = ['http://./']
    def start_requests(self):
        yield scrapy.Request(
            url="https://www.walmart.com/browse/hair-care/hair-color/1085666_3147628_5801378?povid=BeautyGlobalNav_Beauty_HairColor",
            callback=self.parse,
        )

    def parse(self, response):
        open_in_browser(response)
