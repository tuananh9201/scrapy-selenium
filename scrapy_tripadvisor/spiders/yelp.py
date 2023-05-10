from pathlib import Path

import scrapy
from scrapy_tripadvisor.items import ScrapyYelpItem
# from scrapy_selenium import SeleniumRequest
import json
from cssselect.parser import SelectorSyntaxError
from datetime import datetime


class TripadvisorSpider(scrapy.Spider):
    name = "yelp"
    fullsite = True
    pagination_selector = "//div[contains(@class,'pagination-link-container')]/span/a/@href"
    path_selectors = [
        "//h3/span/a/@href"
    ]

    def start_requests(self):
        urls = [
            "https://www.yelp.com/search?find_desc=Chinese&find_loc=Australia",

        ]
        for url in urls:
            # yield SeleniumRequest(url=url, callback=self.parse)
            # yield scrapy.Request(url=url, callback=self.parse)
            yield self.yield_next(url, scrape_depth=0)

    def parse(self, response):
        # titles = response.xpath("//div[contains(@class,'businessName__')]/div/h3/span/a/text()")
        scrape_depth = response.meta.get("scrape_depth", 0)
        if scrape_depth == len(self.path_selectors):
            print("On final page")
            data = self.parse_item(response)
            yield data
        else:
            if self.pagination_selector:
                next_pages = self.extract_links(
                    response, self.pagination_selector)
                if next_pages:
                    # if not self.pagination_list:
                    #     next_pages = [next_pages[0]]
                    print("get all page: ", next_pages)
                    for next_page in next_pages:
                        next_page = self.construct_pagination_url(
                            response, next_page)
                        print("got pagination page %s", next_page)
                        yield self.yield_next(response.urljoin(next_page), scrape_depth)
                print("Not on final page, looking for follow-link with path: %s",
                      self.path_selectors[scrape_depth])
                next_links = self.extract_links(
                    response, self.path_selectors[scrape_depth])
                for link in next_links:
                    yield self.yield_next(response.urljoin(link), scrape_depth + 1)

    def base_data(self, url):
        data = ScrapyYelpItem()
        data["source_url"] = url
        data["scrape_datetime"] = datetime.utcnow().strftime(
            '%Y-%m-%dT%H:%M:%SZ')
        return data

    def try_parse_json(self, text):
        try:
            return json.loads(str(text).strip())
        except:
            pass
        return None

    def parse_item(self, response):
        # https://www.yelp.com/biz/queen-bee-indonesian-and-chinese-munno-para-west?osq=Chinese
        # item = ScrapyYelpItem()
        # item["name"] = response.xpath("//title/text()").get()
        # item['address'] = response.xpath(
        #     "//aside/section/div/div[2]/div/div/p[2]/text()").get()
        # yield item
        scripts_data = response.xpath("//script[@type='application/ld+json']")
        name = response.xpath("//h1/text()").get()
        data = self.base_data(url=response.url)
        for script_text in scripts_data:
            text = script_text.xpath("text()").get()
            if text:
                json_data = self.try_parse_json(text=text)
                if json_data:
                    script_data_type = json_data["@type"]
                    name_json = json_data.get("name")
                    if name_json and script_data_type == "Restaurant":
                        aggregateRatingRaw = json_data.get("aggregateRating")
                        review_count = 0
                        website_uri = response.xpath(
                            "//aside/section/div/div[1]//h2/a/text()").get()
                        aggregateRating = 0
                        if aggregateRatingRaw:
                            aggregateRating = aggregateRatingRaw.get(
                                "ratingValue", 0)
                            review_count = aggregateRatingRaw.get(
                                "reviewCount")
                        data['name'] = name or name_json
                        data['telephone'] = json_data.get("telephone")
                        data['description'] = json_data.get("description", "")
                        data['address'] = json_data.get("address", {})
                        data['aggregateRating'] = aggregateRating
                        data['image'] = json_data.get("image", "")
                        data['priceRange'] = json_data.get("priceRange", "")
                        data["website_uri"] = website_uri
                        data["servesCuisine"] = json_data.get("servesCuisine")
                        data["reviewCount"] = review_count

        return data

    def extract_links(self, response, path_selector):
        """
        method for handling extract link logic in different scenarios

        :param response:
        :param path_selector:
        :return:
        """
        next_links = []
        # What is the link to follow?
        print("looking for follow-link")
        if path_selector == "redirect":
            print("checking for redirect")
            next_links.append(self.get_redirect_url(response))
        else:
            try:
                print("Trying to get next page from xpath")
                next_links = response.xpath(path_selector).extract()
            except (ValueError, TypeError):
                try:
                    print("Trying to get next page from css")
                    next_links = response.css(path_selector).extract()
                except (SelectorSyntaxError, TypeError):
                    print("Trying to get next page from regex")
                    next_links = self.get_regex(response, path_selector)

            if next_links and not self.fullsite:
                next_links = [next_links[0]]

        print("got next links: %s from page: %s, with selector: %s",
              next_links, response.url, path_selector)
        return next_links

    def yield_next(self, url, scrape_depth):
        """
        method to return the next page, checks for splash and handles the scrape_depth

        :param url:
        :param scrape_depth:
        :return:
        """
        print("Scraping page %s", url)
        return scrapy.Request(url,
                              callback=self.parse,
                              meta={"scrape_depth": scrape_depth}
                              )

    def construct_pagination_url(self, response, next_page):
        print("Constructing generic pagination url")
        return next_page

    def close(self, reason):
        print('****** CLOSE', reason)
