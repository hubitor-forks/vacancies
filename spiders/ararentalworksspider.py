import scrapy
from items import MultyItem
from scrapy_playwright.page import PageMethod
from datetime import datetime
import w3lib.html

cookies = {
    'datadome': '5xW4pdtoox2kYZJ9Smnq0ONAsnH0N5~EGujyNUhSfzhWebQIctZJsnN8Rf2n4PWWMvXti7kkLI~Z5VaG~PjO8zIR8Q9Rb0bv7dzJBqblFhg7bOkTU79_aO-5zhprSOah',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Host': 'careers.ararentalworks.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
    'Accept-Language': 'ru',
    'Referer': 'https://careers.ararentalworks.com/jobs/?keywords=dispatcher&pos_flt=0&location=United+States&location_completion=&location_type=&location_text=&location_autocomplete=true&radius=320&sort=start',
    'Connection': 'keep-alive',
}

class ArarentalWorksSpider(scrapy.Spider):
    name = 'ararentalworks'
    allowed_domains = ['careers.ararentalworks.com']

    page = 1

    start_urls = ['https://careers.ararentalworks.com/jobs/?keywords=truck+dispatcher&pos_flt=0&location=United+States&location_completion=&location_type=&location_text=United+States&location_autocomplete=true&radius=320&sort=start']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                # headers=headers,
                # cookies=cookies,
                meta={
                    'playwright': True,
                    'playwright_include_page': True,
                    'playwright_page_methods': [
                        PageMethod("evaluate","setPagination(2,1);searchJobs(2,true);"),
                        PageMethod("wait_for_timeout", 10000),
                    ],
                    'errback': self.errback,
                },
                callback=self.parse
            )

    def parse(self, response):
        jobs = response.css('.job-result-tiles').css('.job-main-data')
        for job in jobs:
            img = job.css('img::attr(src)').get()
            print(img)

    async def errback(self, failure):
        page = failure.request.meta["playwright_page"]
        await page.close()