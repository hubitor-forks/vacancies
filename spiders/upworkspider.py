import scrapy
import w3lib.html

from items import MultyItem
from datetime import datetime

class UpWorkSpider(scrapy.Spider):
    name = 'upwork'

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'HTTPCACHE_ENABLED': True,
    }

    curr_page = 10

    def start_requests(self):
        yield scrapy.Request(
            url=f'https://www.upwork.com/search/jobs/url?q=truck+dispatcher&sort=recency&per_page={self.curr_page}',
            method='GET',
            dont_filter=True,
            callback=self.parse_page)

    def parse_page(self, response):
        jobs = response.json().get('searchResults').get('jobs')
        print(len(jobs))
        # job_tile = response.xpath('//div[contains(@data-test,"job-tile-list")]')
        # job_items = job_tile.css('.up-card-section')

        # for item in job_items:
        #     items = MultyItem()
        #     source_id = item.css('::attr(data-test-key)').get()
        #     link = 'https://www.upwork.com' + item.css('a::attr(href)').get()
        #     salary = item.xpath('//div[contains(@data-test,"job-type")]').css('::text').get()
        #     shift = item.xpath('//div[contains(@data-test,"duration")]').css('::text').get()
        #     description = item.css('.mt-10::text').get()

        #     yield items

        # next_page = response.css('.job-search-pagination ul li:nth-child(8) button').get()
        # print(next_page)
        # if next_page is None:
        #     self.curr_page += 1
        #     yield response.follow(
        #             url=f'https://www.upwork.com/nx/jobs/search/?q=dispatcher&sort=recency&page={self.curr_page}',
        #             headers=headers,
        #             cookies=cookies,
        #             callback=self.parse_page)
