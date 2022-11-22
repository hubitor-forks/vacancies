import scrapy
import w3lib.html
from datetime import datetime
from items import MultyItem


class GlassDoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['glassdoor.com']
    page_count = 1

    def start_requests(self):
        yield scrapy.Request(
            'https://www.glassdoor.com/Job/united-states-truck-dispatcher-jobs-SRCH_IL.0,13_IN1_KO14,30_IP1.htm?fromAge=1&includeNoSalaryJobs=true',
            dont_filter=True,
            callback=self.parse_page)

    def parse_page(self, response, **kwargs):
        list_elements = response.css('li.react-job-listing')
        for list_item in list_elements:
            title = list_item.css('.job-search-key-1rd3saf span::text').get()
            company = list_item.css('a.jobLink span::text').get()
            salary = list_item.css('.job-search-key-1a46cm1 span::text').get()
            location = list_item.css(
                '.job-search-key-1mn3dn8 .e1rrn5ka4::text').get()
            job_post_link = list_item.css(
                '.jobLink').xpath('@href').get()
            source_id = list_item.css('::attr(data-id)').get()

            item = MultyItem()

            item['source_id'] = source_id
            item['position'] = title
            item['company'] = company
            item['location'] = location
            item['salary'] = '' if salary is None else salary
            item['schedule'] = ''
            item['short_description'] = ''
            item['full_description'] = ''
            item['link'] = ('https://www.glassdoor.com' + job_post_link)
            item['website'] = 'glassdoor'
            item['created_at'] = datetime.now()

            yield scrapy.Request('https://www.glassdoor.com' + job_post_link, callback=self.parse, cb_kwargs={'item': item})

        next_page = response.css('.pageContainer .nextButton::attr(disabled)').get()
        if next_page is None:
            self.page_count += 1
            yield response.follow(
                f'https://www.glassdoor.com/Job/united-states-truck-dispatcher-jobs-SRCH_IL.0,13_IN1_KO14,30_IP{self.page_count}.htm?fromAge=1&includeNoSalaryJobs=true',
                callback=self.parse_page)

    def parse(self, response, item):
        description = w3lib.html.remove_tags(response.css('#JobDescriptionContainer .desc').get())
        logo_url = response.css('.css-13u5hxa img::attr(data-original)').get()

        item['short_description'] = description
        item['full_description'] = description
        item['logo_url'] = '' if logo_url is None else logo_url

        yield item