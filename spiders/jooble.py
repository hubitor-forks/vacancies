import scrapy
from scrapy.http.request.json_request import JsonRequest
import w3lib.html
from datetime import datetime
from items import MultyItem


class JoobleSpider(scrapy.Spider):
    name = 'jooble'
    allowed_domains = ['jooble.org']

    url = 'https://jooble.org/api/serp/jobs'

    def start_requests(self):
        for tag in range(1, 4):
            yield JsonRequest(self.url, method='POST', dont_filter=True, data=get_body(tag, 1),
                                 callback=self.parse_page, cb_kwargs={'tag': tag, 'page': 1})

    def parse_page(self, response, tag, page):
        jobs = response.json().get('jobs')
        if len(jobs) == 0:
            return

        for job in jobs:

            posting_day = job.get('dateCaption')
            if ('day' in posting_day) or ('month' in posting_day) or ('year' in posting_day):
                continue

            item = MultyItem()

            schedule = ''
            if tag == 1:
                schedule = 'Full-time'
            elif tag == 2:
                schedule = 'Temporary'
            else:
                schedule = 'Part-time'

            item['position'] = w3lib.html.remove_tags(job.get('position'))
            item['company'] = job.get('company').get('name')
            item['location'] = job.get('location').get('name')
            item['salary'] = job.get('salary')
            item['schedule'] = schedule
            item['short_description'] = w3lib.html.remove_tags(job.get('content')).replace('&nbsp;...', '').strip()
            item['full_description'] = w3lib.html.remove_tags(job.get('content')).replace('&nbsp;...', '').strip()
            item['link'] = 'https://jooble.org/desc/' + job.get('uid')
            item['source_id'] = job.get('uid')
            item['logo_url'] = '' if job.get('company').get('logoUrl') is None else job.get('company').get('logoUrl')
            item['website'] = 'jooble'
            item['created_at'] = datetime.now()

            yield item

        yield JsonRequest(self.url, method='POST', dont_filter=True, data=get_body(tag, page+1),
                              callback=self.parse_page, cb_kwargs={'tag': tag, 'page': page + 1})


def get_body(tag, page):
    return {
        'search': 'trucking dispatcher',
        'region': 'United States',
        'regionId': 0,
        'isCityRegion': False,
        'jobTypes': [tag],
        'coords': None,
        'date': 8,
        'page': page,
        'isRemoteSerp': False,
    }
