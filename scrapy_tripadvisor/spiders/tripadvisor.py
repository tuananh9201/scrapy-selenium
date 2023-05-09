from pathlib import Path

import scrapy
from scrapy_tripadvisor.items import ScrapyTripadvisorItem
# from scrapy_selenium import SeleniumRequest


class TripadvisorSpider(scrapy.Spider):
    name = "tripadvisor"

    def start_requests(self):
        urls = [
            "https://www.tripadvisor.com/Hotels-g255055-Australia-Hotels.html"
        ]
        for url in urls:
            # yield SeleniumRequest(url=url, callback=self.parse)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # titles = response.xpath("//div[@class='listing_title ']/a/text()")
        listing = response.xpath("//div[@class='listing_title ']/a")
        item = ScrapyTripadvisorItem()
        for item_crawl in listing:
            item["name"] = item_crawl.xpath("text()").get()
            link = item_crawl.xpath("@href").get()
            item['address'] = link
            yield item

    # def parse_item(self, response):
    #     item = ScrapyTripadvisorItem()
    #     for item_crawl in listing:
    #         item["name"] = item_crawl.xpath("text()").get()
    #         link = item_crawl.xpath("@href").get()
    #         item['address'] = link
    #         yield item
