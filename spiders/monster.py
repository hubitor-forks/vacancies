import scrapy
from scrapy.http.request.json_request import JsonRequest
import w3lib.html
from datetime import datetime
from items import MultyItem


class MonsterSpider(scrapy.Spider):
    name = 'monster'
    allowed_domains = ['monster.com']
    start_urls = [
        'https://appsapi.monster.io/jobs-svx-service/v2/monster/search-jobs/samsearch/en-US?apikey'
        '=AE50QWejwK4J73X1y1uNqpWRr2PmKB3S']

    page_count = 0
    curr_time = datetime.now()

    def start_requests(self):
        yield JsonRequest(
            url=self.start_urls[0],
            method='POST',
            dont_filter=True,
            data=get_data(0),
            callback=self.parse
        )

    def parse(self, response, **kwargs):
        job_results = response.json().get('jobResults')

        for post in job_results:
            job_posting = post.get('jobPosting')
            item = MultyItem()
            url = job_posting.get('url')
            description = w3lib.html.remove_tags(job_posting.get('description'))
            logo_url = job_posting.get('hiringOrganization').get('logo_url')
            source_id = post.get('jobId')
            base_salary = job_posting.get('baseSalary')
            salary = ''
            if base_salary is not None:
                value = base_salary.get('value')
                if value.get('value') is not None:
                    salary = '$' + str(value.get('value')) + ' / ' + value.get('unitText')
                elif value.get('minValue') is not None:
                    salary = '$' + str(value.get('minValue')) + ' - $' + str(value.get('maxValue')) + ' / ' + value.get(
                        'unitText')

            schedule = ', '.join([item.get('translation').strip() for item in post.get('fieldTranslations')])
            title = job_posting.get('title')
            company = job_posting.get('hiringOrganization').get('name')
            job_location = job_posting.get('jobLocation')[0].get('address')
            location = job_location.get('addressLocality') + ', ' + job_location.get('addressRegion')

            item['source_id'] = source_id
            item['position'] = title
            item['company'] = company
            item['location'] = location
            item['salary'] = salary
            item['schedule'] = schedule
            item['short_description'] = description
            item['full_description'] = description
            item['logo_url'] = '' if logo_url is None else logo_url
            item['link'] = url
            item['website'] = 'monster'
            item['created_at'] = datetime.now()

            yield item

        # Next page
        if len(job_results) > 0:
            self.page_count += 1
            yield JsonRequest(
                url=self.start_urls[0],
                method='POST',
                dont_filter=True,
                data=get_data(self.page_count),
                callback=self.parse
            )


def get_data(page):
    return {
        'jobQuery': {
            'query': 'Dispatcher, Broker',
            'locations': [
                {
                    'country': 'us',
                    'address': 'USA',
                    'radius': {
                        'unit': 'mi',
                        'value': 20,
                    },
                },
            ],
            'activationRecency': 'today',
        },
        'jobAdsRequest': {
            'position': [
                1, 2, 3, 4, 5, 6, 7, 8, 9,
            ],
            'placement': {
                'channel': 'WEB',
                'location': 'JobSearchPage',
                'property': 'monster.com',
                'type': 'JOB_SEARCH',
                'view': 'SPLIT',
            },
        },
        'fingerprintId': '722e243a6e80a8aebb270db5b24876f4',
        'offset': 50 * page,
        'pageSize': 50,
        'histogramQueries': [
            'count(company_display_name)',
            'count(employment_type)',
        ],
    }
