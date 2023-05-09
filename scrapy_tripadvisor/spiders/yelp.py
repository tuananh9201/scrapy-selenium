from pathlib import Path

import scrapy
from scrapy_tripadvisor.items import ScrapyYelpItem
# from scrapy_selenium import SeleniumRequest
import urllib


class TripadvisorSpider(scrapy.Spider):
    name = "yelp"

    def start_requests(self):
        urls = [
            "https://www.yelp.com/search?find_desc=Chinese&find_loc=Australia+Plains%2C+South+Australia%2C+Australia"
        ]
        for url in urls:
            # yield SeleniumRequest(url=url, callback=self.parse)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # titles = response.xpath("//div[contains(@class,'businessName__')]/div/h3/span/a/text()")
        links = response.xpath(
            "//div[contains(@class,'businessName__')]/div/h3/span/a/@href")
        for link in links:
            url = "https://www.yelp.com"+link.get()
            print('****', url)
            yield scrapy.Request(url=url, callback=self.parse_item)

    def parse_item(self, response):
        # https://www.yelp.com/biz/queen-bee-indonesian-and-chinese-munno-para-west?osq=Chinese
        item = ScrapyYelpItem()
        item["name"] = response.xpath("//title/text()").get()
        item['address'] = response.xpath(
            "//aside/section/div/div[2]/div/div/p[2]/text()").get()
        yield item
