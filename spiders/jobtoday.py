import scrapy
from datetime import datetime
from items import MultyItem


class JobtodaySpider(scrapy.Spider):
    name = 'jobtoday'
    allowed_domains = ['jobtoday.com']
    start_urls = ['https://jobtoday.com/']

    page_count = 1

    def start_requests(self):
        yield scrapy.Request('https://jobtoday.com/us/jobs-dispatcher-broker', callback=self.parse)

    def parse(self, response, **kwargs):
        container = response.css('div:nth-child(1) > div.jt-container section:nth-child(2) ul')
        if container is not None:
            for card in container.css('li'):
                upload_date = card.xpath('//span[contains(@data-testid,"job-card_update-date")]').get()
                if ('day' in upload_date) or ('month' in upload_date) or ('year' in upload_date):
                    continue

                item = MultyItem()

                url = card.css('a::attr(href)').get()
                position = card.css('.line-clamp-1::text').get()
                company = card.css('.line-clamp-1.text-sm.not-italic::text').get()
                location = card.css('.text-sm.line-clamp-1.text-jt-gray-400::text').get()
                salary = card.css('.text-jt-primary::text').get()
                description = card.css('.line-clamp-2::text').get().strip().replace('\xa0', '')

                item['source_id'] = ''
                item['position'] = position
                item['company'] = company
                item['location'] = location
                item['salary'] = '' if salary is None else salary
                item['schedule'] = ''
                item['short_description'] = description
                item['full_description'] = description
                item['logo_url'] = ''
                item['link'] = url
                item['website'] = 'jobtoday'
                item['created_at'] = datetime.now()

                yield item
                # yield scrapy.Request(url, callback=self.parse_page, cb_kwargs={'item': item})

        # Next page
        tabs = response.css('.tabs')
        next_page = tabs.xpath('//a[contains(@aria-label,"Next page")]').get()
        if next_page is not None:
            self.page_count += 1
            next_page = f'https://jobtoday.com/us/jobs-dispatcher-broker?page={self.page_count}'
            yield response.follow(next_page, callback=self.parse)

    # def parse_page(self, response, item):
    #     if 'ziprecruiter' in response.url:
    #         # yield scrapy.Request(response.url, callback=self.ziprecruiter_parse, cb_kwargs={'item': item})
    #         yield item
    #     elif 'click.appcast.io' in response.url:
    #         yield scrapy.Request(response.url, callback=self.linkedin_parse, cb_kwargs={'item': item})
    #     else:
    #         yield item
    #
    # def ziprecruiter_parse(self, requests, item):
    #     schedule = requests.css('.job_tile .employment_type::text').get()
    #     logo_url = requests.css('.job_tile .company_details img')
    #
    #     item['schedule'] = schedule
    #     item['logo_url'] = logo_url
    #
    #     yield item
    #
    # def linkedin_parse(self, requests, item):
    #     print('linkedin')
    #     schedule = requests.css('.description__job-criteria-text::text').get()
    #     logo_url = requests.css('.top-card-layout .artdeco-entity-image::attr(src)').get()
    #
    #     item['schedule'] = schedule
    #     item['logo_url'] = logo_url
    #
    #     yield item
