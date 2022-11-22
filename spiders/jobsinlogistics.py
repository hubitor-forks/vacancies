import scrapy
from datetime import datetime
from items import MultyItem


class JobsInLogisticsSpider(scrapy.Spider):
    name = 'jobsinlogistics'
    allowed_domains = ['jobsinlogistics.com']
    start_urls = ['https://www.jobsinlogistics.com/cgi-local/search.cgi?TypeOfUser=browse&TypeOfUser=browse&what=dispatcher%2C+broker']

    is_next_page = True
    curr_time = datetime.now()

    # custom_settings = {
    #     'DEPTH_LIMIT': 4, # avoid IP blocking
    #     'CONCURRENT_REQUESTS': 1,
    #     'DOWNLOAD_DELAY': 30
    # }

    def start_requests(self):
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse
        )

    def parse(self, response, **kwargs):
        for card in response.css('a.job'):
            star = card.css('h2 img').get()

            if star is not None:
                continue

            url = card.attrib['href']

            item = MultyItem()
            item['source_id'] = url.split('=')[2]
            item['position'] = card.css('.job-details h2::text').get()
            item['company'] = card.css('.job-company::text').get()
            item['location'] = card.css('.job-location::text').get()
            item['salary'] = ''
            item['schedule'] = ''
            item['short_description'] = card.css('.job-description::text').get()
            item['full_description'] = card.css('.job-description::text').get()
            item['link'] = url
            item['website'] = 'jobsinlogistics'
            item['created_at'] = self.curr_time

            yield scrapy.Request(url, callback=self.parce_page, cb_kwargs={'item': item})

        next_page = response.css('.next::attr(href)').get()
        if next_page is not None and self.is_next_page:
            yield response.follow(
                next_page,
                callback=self.parse
            )

    def parce_page(self, response, item):
        posted_date = datetime.strptime(response.css('.posted-date::text').get(), '%m/%d/%y')

        if posted_date.day != datetime.now().day:
            self.is_next_page = False
            return

        item['schedule'] = response.css('.job-type::text').get()
        item['logo_url'] = response.css('.jobdesc-image::attr(src)').get()

        yield item
