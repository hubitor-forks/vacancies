import scrapy
import w3lib.html

from items import MultyItem
from datetime import datetime

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Host': 'www.work.ua',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
    'Accept-Language': 'ru',
    'Connection': 'keep-alive',
}

class WorkUaSpider(scrapy.Spider):
    name = 'workUa'

    curr_page = 1

    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
    }

    def start_requests(self):
        yield scrapy.Request(
            url=f'https://www.work.ua/ru/jobs-truck+dispatcher/?days=122&page={self.curr_page}',
            headers=headers,
            callback=self.parse_page)

    def parse_page(self, response):
        job_list = response.css('#pjax-job-list')
        job_items = job_list.css('.card-hover')

        for item in job_items:
            items = MultyItem()

            a_link = item.css('h2 a')
            link = 'https://www.work.ua' + a_link.css('::attr(href)').get()
            source_id = link.split('/')[5]
            img_link = item.css('img::attr(src)').get()
            position = a_link.css('::text').get()
            salary = item.css('div b::text').get()
            schedule = item.xpath('//*[@id="pjax-job-list"]/div[2]/p/text()[1]').get()
            short_description = item.xpath('//*[@id="pjax-job-list"]/div[2]/p/text()[2]').get()

            items['source_id'] = source_id
            items['logo_url'] = img_link
            items['position'] = position
            items['salary'] = salary
            items['schedule'] = schedule.strip()
            items['short_description'] = short_description.strip()
            items['website'] = self.name
            items['created_at'] = datetime.now()
            items['link'] = link

            yield scrapy.Request(
                url= link,
                headers=headers,
                callback=self.parse,
                cb_kwargs={'items':items}
            )

        if len(job_list) > 0:
            self.curr_page += 1
            yield response.follow(
                url=f'https://www.work.ua/ru/jobs-truck+dispatcher/?days=122&page={self.curr_page}',
                headers=headers,
                callback=self.parse_page)

    def parse(self, response, items):
        full_description = w3lib.html.remove_tags(response.css('#job-description').get().strip()).strip()

        company = response.css('#center > div > div.row.row-print > div.col-md-8.col-left > div:nth-child(3) > div.card.wordwrap > p:nth-child(4) > a > b::text').get()
        if company is None:
            company = response.css('#center > div > div.row.row-print > div.col-md-8.col-left > div:nth-child(3) > div.card.wordwrap > p:nth-child(5) > a > b::text').get()

        # location = response.xpath('//*[@id="center"]/div/div[2]/div[1]/div[3]/div[1]/p[4]/text()').get()

        items['full_description'] = full_description
        items['company'] = company
        items['location'] = ''

        items['shift'] = ''
        items['updated_at'] = ''

        yield items
