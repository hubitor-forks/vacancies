import scrapy
import w3lib.html

from items import MultyItem
from datetime import datetime

headers = {
    'Accept': '*/*',
    'Host': 'www.linkedin.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
    'Accept-Language': 'ru',
    'Referer': 'https://www.linkedin.com/jobs/search?keywords=Truck%20Dispatcher&location=%D0%A1%D0%BE%D0%B5%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%A8%D1%82%D0%B0%D1%82%D1%8B%20%D0%90%D0%BC%D0%B5%D1%80%D0%B8%D0%BA%D0%B8&locationId=&geoId=103644278&f_TPR=r86400&position=1&pageNum=0',
    'Connection': 'keep-alive',
}

class LinkedInSpider(scrapy.Spider):
    name = 'linkedin'

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    pass_page_count = 0

    def start_requests(self):
        yield scrapy.Request(
            url=f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Truck%20Dispatcher&location=%D0%A1%D0%BE%D0%B5%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%A8%D1%82%D0%B0%D1%82%D1%8B%20%D0%90%D0%BC%D0%B5%D1%80%D0%B8%D0%BA%D0%B8&locationId=&geoId=103644278&f_TPR=r86400&position=1&pageNum=1&start={self.pass_page_count*25}',
            headers=headers,
            callback=self.parse_page)

    def parse_page(self, response):
        items = response.css('li')
        for item in items:
            position = item.css('.base-search-card__title::text').get().strip()
            url = item.css('a::attr(href)').get()
            source_id = item.css('div::attr(data-tracking-id)').get()

            items = MultyItem()
            items['source_id'] = source_id
            items['position'] = position
            items['link'] = url
            items['website'] = self.name
            items['position'] = position
            items['created_at'] = datetime.now()

            yield scrapy.Request(
                url=url,
                headers=headers,
                callback=self.parse,
                cb_kwargs={'items':items}
            )

        if len(items) > 0:
            self.pass_page_count += 1
            url = f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Truck%20Dispatcher&location=%D0%A1%D0%BE%D0%B5%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%A8%D1%82%D0%B0%D1%82%D1%8B%20%D0%90%D0%BC%D0%B5%D1%80%D0%B8%D0%BA%D0%B8&locationId=&geoId=103644278&f_TPR=r86400&position=1&pageNum=1&start={self.pass_page_count*25}'
            yield response.follow(
                url=f'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=Truck%20Dispatcher&location=%D0%A1%D0%BE%D0%B5%D0%B4%D0%B8%D0%BD%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5%20%D0%A8%D1%82%D0%B0%D1%82%D1%8B%20%D0%90%D0%BC%D0%B5%D1%80%D0%B8%D0%BA%D0%B8&locationId=&geoId=103644278&f_TPR=r86400&position=1&pageNum=1&start={self.pass_page_count*25}',
                headers=headers,
                callback=self.parse_page)

    def parse(self, response, items):
        topcard = response.css('.topcard__flavor')

        company = topcard[0].css('a::text').get().strip()
        location = topcard[1].css('::text').get().strip()
        description = w3lib.html.remove_tags(response.css('.decorated-job-posting__details .description').get().strip()).strip()
        schedule = response.css('.description__job-criteria-list li:nth-child(2) span::text').get()
        img_link = response.css('.top-card-layout__card a img::attr(data-delayed-url)').get()

        items['company'] = company
        items['location'] = location
        items['short_description'] = description
        items['full_description'] = description
        items['schedule'] = schedule.strip() if schedule is not None else ''
        items['logo_url'] = img_link

        items['salary'] = ''
        items['shift'] = ''
        items['updated_at'] = ''

        yield items
