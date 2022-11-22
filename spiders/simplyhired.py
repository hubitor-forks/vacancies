import scrapy
from datetime import datetime
from items import MultyItem


class SimplyHiredSpider(scrapy.Spider):
    name = 'simplyhired'
    allowed_domains = ['simplyhired.com']
    start_urls = ['https://www.simplyhired.com/search?q=dispatcher%2C+broker&fdb=1&sb=dd&pn=1']

    page = 0

    def parse(self, response, **kwargs):
        for card in response.xpath('//div[contains(@class,"card")]'):
            item = MultyItem()

            key = card.attrib['data-jobkey']
            description = card.css('.jobposting-snippet::text').get()
            url = f'https://www.simplyhired.com/job/{key}'
            req_url = f'https://www.simplyhired.com/api/job?key={key}'

            item['source_id'] = key
            item['short_description'] = description
            item['full_description'] = description
            item['link'] = url

            yield scrapy.Request(req_url, callback=self.parse_page, cb_kwargs={'item': item})

        next_page = response.css('.next-pagination').get()
        if next_page is not None:
            self.page += 1
            yield response.follow(f'https://www.simplyhired.com/search?q=dispatcher%2C+broker&fdb=1&sb=dd&pn={self.page}', callback=self.parse)

    def parse_page(self, response, item):
        data = response.json()

        logo_url = data.get('job').get('logoUrl')

        item['position'] = data.get('job').get('title')
        item['company'] = data.get('job').get('company')
        item['location'] = data.get('job').get('location')
        item['salary'] = '' if data.get('salaryInfo') is None else data.get('salaryInfo')
        item['schedule'] = data.get('job').get('jobType')
        item['logo_url'] = '' if logo_url is None else 'https://www.simplyhired.com' + logo_url
        item['website'] = 'simplyhired'
        item['created_at'] = datetime.now()

        yield item
