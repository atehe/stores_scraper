import scrapy

from scrapy.utils.response import open_in_browser


class WalmartPlaywrightSpider(scrapy.Spider):
    name = "walmart_playwright"
    # allowed_domains = ['.']
    # start_urls = ['http://./']
    custom_settings = {
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
    }

    def start_requests(self):

        # GET request
        yield scrapy.Request(
            "https://www.walmart.com/browse/home-improvement/hand-tool-sets/1072864_1031899_1067609_1067747",
            meta={"playwright": True, "playwright_include_page": True},
        )

    async def parse(self, response):
        open_in_browser(response)
        page = response.meta["playwright_page"]
        next_rel_rul = response.xpath("//a[@aria-label='Next Page']/@href").get()
        url = f"https://www.walmart.com{next_rel_rul}"
        await page.close()
        yield scrapy.Request(
            url=url,
            meta={"playwright": True, "playwright_include_page": True},
            callback=self.parse,
        )
