import scrapy
import w3lib.html
import random

from items import MultyItem
from datetime import datetime

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Host': 'www.salary.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
    'Accept-Language': 'ru',
    'Referer': 'https://www.salary.com/',
    'Connection': 'keep-alive',
}

class SalarySpider(scrapy.Spider):
    name = 'salary'

    curr_page = 1

    def start_requests(self):
        yield scrapy.Request(
            url=f'https://www.salary.com/job/searchresults?jobtitle=truck+dispatcher&posttime=1%2520Day&pg={self.curr_page}',
            headers=headers,
            callback=self.parse_page)

    def parse_page(self, response):
        search_items = response.css('.sal-search-results-list')

        for item in search_items:
            items = MultyItem()

            a_link = item.css('div:nth-child(1) div:nth-child(2) a')

            position = a_link.css('::text').get()
            link = a_link.css('::attr(href)').get()
            short_description = item.css('.sal-company-location li:nth-child(3) span::text').get().strip()

            items['position'] = position
            items['link'] = link
            items['created_at'] = datetime.now()
            items['website'] = self.name
            items['short_description'] = short_description

            if 'www.salary.com' in link:
                yield scrapy.Request(
                    url=link,
                    dont_filter=True,
                    callback=self.parse_salary,
                    cb_kwargs={'items':items})

        if len(search_items) > 0:
            self.curr_page += 1

            yield response.follow(
                url=f'https://www.salary.com/job/searchresults?jobtitle=truck+dispatcher&posttime=1%2520Day&pg={self.curr_page}',
                headers=headers,
                callback=self.parse_page)

    def parse_salary(self, response, items):
        url = response.url

        head = response.css('.sa-layout-section-hed')

        source_id = url.split('/')[-1].split('?')[0]
        company = head.css('a span::text').get()
        location = head.css('#sal-hired-organization-address::text').get()
        schedule = head.css('#sal-job-type::text').get()
        full_description = w3lib.html.remove_tags(response.css('#sal-job-description').get().strip()).strip()
        salary = ''
        logo_url = ''

        items['source_id'] = source_id
        items['company'] = company
        items['location'] = location
        items['schedule'] = schedule
        items['full_description'] = full_description
        items['salary'] = salary
        items['logo_url'] = logo_url

        yield items
