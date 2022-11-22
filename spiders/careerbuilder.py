import scrapy
from datetime import datetime
from items import MultyItem
import w3lib.html


class CareerBuilderSpider(scrapy.Spider):
    name = 'careerbuilder'
    page_number = 1

    allowed_domains = ['careerbuilder.com']

    def start_requests(self):
        yield scrapy.Request(f'https://www.careerbuilder.com/jobs?cb_apply=false&cb_workhome=false&emp=&keywords'
                             f'=Dispatcher%2C+Broker&location=Us&page_number={self.page_number}&pay=&posted=1&sort=date_desc',
                             callback=self.parse_page)

    def parse_page(self, response, **kwargs):
        for job in response.css('.data-results-content-parent'):
            if job is None:
                break

            item = MultyItem()

            item['link'] = 'https://www.careerbuilder.com' + job.css('a::attr(href)').get()
            item['source_id'] = job.css('a::attr(href)').get().split('/')[2]
            item['logo_url'] = job.css('.data-results-img img::attr(data-src)').get()
            yield scrapy.Request(item['link'], callback=self.parse, cb_kwargs={'item': item})

        # Next page
        next_page = response.css('#load_more_jobs button').get()
        if next_page:
            self.page_number += 1
            yield response.follow(f'https://www.careerbuilder.com/jobs?cb_apply=false&cb_workhome=false&emp=&keywords'
                                  f'=Dispatcher%2C+Broker&location=Us&page_number={self.page_number}&pay=&posted=1&sort=date_desc',
                                  callback=self.parse_page)

    def parse(self, response, item):
        data_details = response.css('.data-display-header_info-content .data-details span::text').getall()
        description = w3lib.html.remove_tags(response.xpath('//div[contains(@aria-labelledby,"jobDetails")]').css('.col').get()).strip()

        item['position'] = response.css('.data-display-header_info-content h2::text').get()
        item['company'] = data_details[0]
        item['location'] = data_details[1]
        item['salary'] = response.css('#cb-salcom-info .block::text').get().strip()
        item['schedule'] = data_details[2]
        item['short_description'] = description
        item['full_description'] = description
        item['link'] = response.url
        item['website'] = 'careerbuilder'
        item['created_at'] = datetime.now()

        yield item

