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


# categories_dict = {
#     "Fresh Food": "https://www.tesco.com/groceries/en-GB/shop/fresh-food/all",
#     "Bakery": "https://www.tesco.com/groceries/en-GB/shop/bakery/all",
#     "Frozen Food": "https://www.tesco.com/groceries/en-GB/shop/frozen-food/all",
#     "Food Cupboard": "https://www.tesco.com/groceries/en-GB/shop/food-cupboard/all",
#     "Drinks": "https://www.tesco.com/groceries/en-GB/shop/drinks/all",
#     "Wine, Beers & Spirits": "https://www.tesco.com/groceries/en-GB/shop/wine-beers-and-spirits/all",
#     "Baby": "https://www.tesco.com/groceries/en-GB/shop/baby/all",
#     "Health & Beauty": "https://www.tesco.com/groceries/en-GB/shop/health-and-beauty/all",
#     "Pets": "https://www.tesco.com/groceries/en-GB/shop/pets/all",
#     "Household": "https://www.tesco.com/groceries/en-GB/shop/household/all",
#     "Home & Ents": "https://www.tesco.com/groceries/en-GB/shop/home-and-ents/all",
# }


class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["www.tesco.com"]

    def start_requests(self):
        # for category, url in categories_dict.items():
        #     yield SeleniumRequest(
        #         url=url, callback=self.parse, meta={"category": category}
        #     )
        yield SeleniumRequest(
            url="https://www.tesco.com/groceries/en-GB/shop/fresh-food/fresh-vegetables?include-children=true",
            callback=self.parse,
        )

    def parse(self, response):
        open_in_browser(response)
        products = response.xpath("//li[contains(@class, 'product-list')]")
        # category = response.meta.get("category")

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
                # "Category": category,
                "Product ID": product_id,
                "Product URL": abs_url,
                "Price": price,
                "Cup Price": cup_price,
            }
        # next_page = response.xpath('//a[@title="Go to results page"]/@href').get()
        # if next_page:
        #     url = f"https://www.tesco.com{next_page}"
        #     yield SeleniumRequest(
        #         url=url, callback=self.parse, meta={"category": category}
        #     )
