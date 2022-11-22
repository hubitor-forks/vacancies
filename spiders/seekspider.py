import scrapy
from scrapy.http.request.json_request import JsonRequest
import w3lib.html

from items import MultyItem
from datetime import datetime

def get_url(page):
    return 'https://www.seek.com.au/api/chalice-search/v4/search?siteKey=AU-Main&sourcesystem=houston&userqueryid=62e5d77f2d2ab2492513c6edf8705551-5959191&userid=51df0696-854d-4a6f-bf5b-66b596a86bd5&usersessionid=51df0696-854d-4a6f-bf5b-66b596a86bd5&eventCaptureSessionId=51df0696-854d-4a6f-bf5b-66b596a86bd5&where=Work+from+home&page=' + str(page) + '&seekSelectAllPages=true&keywords=dispatcher&daterange=3&include=seodata&solId=1dbc2102-ef5b-4713-b743-c79a0f8117ad'

def get_data(id):
    return {
        'operationName': 'GetJobDetails',
        'variables': {
            'jobId': str(id),
            'jobDetailsViewedCorrelationId': 'a945b40a-ac96-4644-9451-f36caf537498',
            'sessionId': '51df0696-854d-4a6f-bf5b-66b596a86bd5',
            'zone': 'anz-1',
            'locale': 'en-AU',
        },
        'query': 'query GetJobDetails($jobId: ID!, $jobDetailsViewedCorrelationId: String!, $sessionId: String!, $zone: Zone!, $locale: Locale!) {\n  jobDetails(\n    id: $jobId\n    tracking: {channel: "WEB", jobDetailsViewedCorrelationId: $jobDetailsViewedCorrelationId, sessionId: $sessionId}\n  ) {\n    job {\n      tracking {\n        adProductType\n        classificationInfo {\n          classificationId\n          classification\n          subClassificationId\n          subClassification\n          __typename\n        }\n        hasRoleRequirements\n        isPrivateAdvertiser\n        locationInfo {\n          area\n          location\n          locationIds\n          __typename\n        }\n        __typename\n      }\n      id\n      title\n      isExpired\n      isLinkOut\n      contactMatches {\n        type\n        value\n        __typename\n      }\n      abstract\n      content(platform: WEB)\n      status\n      listedAt {\n        shortLabel\n        __typename\n      }\n      salary {\n        label\n        __typename\n      }\n      shareLink(platform: WEB, zone: $zone)\n      workTypes {\n        label\n        __typename\n      }\n      advertiser {\n        id\n        name\n        __typename\n      }\n      location {\n        label(locale: $locale, type: LONG)\n        __typename\n      }\n      categories {\n        label\n        __typename\n      }\n      products {\n        branding {\n          id\n          cover {\n            url\n            __typename\n          }\n          thumbnailCover: cover(isThumbnail: true) {\n            url\n            __typename\n          }\n          logo {\n            url\n            __typename\n          }\n          __typename\n        }\n        bullets\n        questionnaire {\n          questions\n          __typename\n        }\n        video {\n          url\n          position\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    companyReviews(zone: $zone) {\n      id\n      name\n      fullName\n      rating\n      reviewCount\n      reviewsUrl\n      __typename\n    }\n    companySearchUrl(zone: $zone)\n    learningInsights(platform: WEB, zone: $zone) {\n      analytics\n      content\n      __typename\n    }\n    sourcr {\n      image\n      imageMobile\n      link\n      __typename\n    }\n    __typename\n  }\n}\n',
    }

class SeekSpider(scrapy.Spider):
    name = 'seek'

    curr_page = 1

    def start_requests(self):
        yield JsonRequest(
            url=get_url(self.curr_page),
            method='GET',
            dont_filter=True,
            callback=self.parse_page)

    def parse_page(self, response):
        jobs = response.json().get('data')

        for item in jobs:
            items = MultyItem()

            source_id = item.get('id')
            position = item.get('title')
            link = 'https://www.seek.com.au/job/' + str(source_id)

            company = item.get('advertiser').get('description')
            logo_url = ''
            if item.get('branding') is not None:
                logo_url = item.get('branding').get('assets').get('logo').get('strategies').get('jdpLogo')

            location = item.get('jobLocation').get('label')

            items['source_id'] = source_id
            items['position'] = position
            items['company'] = company
            items['location'] = location
            items['link'] = link
            items['website'] = self.name
            items['logo_url'] = logo_url
            items['created_at'] = datetime.now()

            yield JsonRequest(
                url='https://www.seek.com.au/graphql',
                method='POST',
                dont_filter=True,
                data=get_data(source_id),
                callback=self.parse,
                cb_kwargs={'items':items})

        if len(jobs) > 0:
            self.curr_page += 1
            yield JsonRequest(
                url=get_url(self.curr_page),
                method='GET',
                dont_filter=True,
                callback=self.parse_page)

    def parse(self, response, items):
        item = response.json().get('data').get('jobDetails').get('job')


        short_description = item.get('abstract')
        full_description = w3lib.html.remove_tags(item.get('content').strip()).strip()
        salary = ''
        if item.get('salary') is not None:
            salary = item.get('salary').get('label')
        schedule = item.get('workTypes').get('label')
        shift = ''

        items['salary'] = salary
        items['schedule'] = schedule
        items['shift'] = shift
        items['short_description'] = short_description
        items['full_description'] = full_description

        yield items
