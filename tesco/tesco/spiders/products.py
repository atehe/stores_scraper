from gc import callbacks
import scrapy
from scrapy_selenium import SeleniumRequest
from scrapy.utils.response import open_in_browser


def extract_product_id(url):
    try:
        last_slash_index = url[::-1].index("/")
        return url[-last_slash_index:]
    except:
        return url


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["www.tesco.com"]

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.tesco.com/groceries/en-GB/shop/fresh-food/all",
            callback=self.parse,
        )

    def parse(self, response):
        print("testing scrapy \n\n\n")
        # open_in_browser(response)
        products = response.xpath("//li[contains(@class, 'product-list')]")

        for product in products:
            name = product.xpath(".//a[@data-auto='product-tile--title']//text()").get()
            rel_url = product.xpath(
                ".//a[@data-auto='product-tile--title']/@href"
            ).get()
            price = "".join(
                product.xpath(
                    ".//div[contains(@class,'price-per-sellable')]//text()"
                ).getall()
            )
            cup_price = "".join(
                product.xpath(
                    ".//div[@class='price-per-quantity-weight']//text()"
                ).getall()
            )
            product_id = extract_product_id(rel_url)
            abs_url = f"https://www.tesco.com{rel_url}"

            yield {
                "Name": name,
                "Product ID": product_id,
                "Product URL": abs_url,
                "Price": price,
                "Cup Price": cup_price,
            }
        next_page = response.xpath('//a[@title="Go to results page"]/@href').get()
        if next_page:
            url = f"https://www.tesco.com{next_page}"
            yield SeleniumRequest(url=url, callback=self.parse)
