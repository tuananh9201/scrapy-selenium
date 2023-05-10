# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BasteItem(scrapy.Item):
    name = scrapy.Field()


class ScrapyTripadvisorItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    address = scrapy.Field()
    pass


class ScrapyYelpItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    address = scrapy.Field()
    description = scrapy.Field()
    telephone = scrapy.Field()
    aggregateRating = scrapy.Field()
    source_url = scrapy.Field()
    image = scrapy.Field()
    scrape_datetime = scrapy.Field()
    priceRange = scrapy.Field()
    website_uri = scrapy.Field()
    servesCuisine = scrapy.Field()
    reviewCount = scrapy.Field()
    pass
