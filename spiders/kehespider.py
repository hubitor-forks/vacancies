import scrapy
from items import MultyItem
from scrapy_playwright.page import PageMethod
from datetime import datetime
import w3lib.html

class KeheSpider(scrapy.Spider):
    name = 'kehe'
    allowed_domains = ['careers.kehe.com']

    page = 1

    start_urls = [f'https://careers.kehe.com/us/en/search-results?keywords=truck%20dispathcer&from={page * 10}&s=1']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod("wait_for_selector", '.jobs-list-item'),
                    ],
                },
                callback=self.parse
            )

    def parse(self, response):
        jobs = response.css('.jobs-list-item')

        for job in jobs:
            items = MultyItem()

            link = job.css('.information > [role="heading"] a::attr(href)').get()
            short_description = job.css('.job-description::text').get()

            items['link'] = link

            items['short_description'] = short_description
            items['website'] = self.name
            items['created_at'] = datetime.now()

            yield response.follow(
                link,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod("wait_for_selector", '.job-description'),
                    ],
                },
                callback=self.parse_page,
                cb_kwargs={'items':items})

        # pagination
        if len(jobs) == 10:
            self.page += 1
            yield response.follow(
                    f'https://careers.kehe.com/us/en/search-results?keywords=truck%20dispathcer&from={self.page * 10}&s=1',
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod("wait_for_selector", '.jobs-list-item'),
                        ],
                    },
                    callback=self.parse
                )


    def parse_page(self, response, items):
        page_posted_date = w3lib.html.remove_tags(response.css('.job-postedDate').get()).replace('Posted Date:', '').strip()
        if page_posted_date != datetime.now().strftime('%m/%d/%Y'):
            return

        position = response.css('.job-title::text').get()
        source_id = w3lib.html.remove_tags(response.css('.jobId').get()).replace('Job Id', '').strip()
        location = w3lib.html.remove_tags(response.css('.job-location').get()).replace('Location', '').strip()
        full_description = w3lib.html.remove_tags(response.css('.job-description').get().strip()).replace('JOB DESCRIPTION', '').strip()
        items['position'] = position
        items['source_id'] = source_id
        items['location'] = location
        items['full_description'] = full_description
        items['company'] = ''
        items['salary'] = ''
        items['schedule'] = 'Full-time'
        items['shift'] = ''
        items['logo_url'] = ''

        yield items


