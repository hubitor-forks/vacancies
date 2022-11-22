import scrapy
from scrapy.http.request.json_request import JsonRequest
import w3lib.html

from items import MultyItem
from datetime import datetime

def get_url(page:int, zip:str):
    return 'https://www.snagajob.com/api/jobs/v1/p4p?sort=date&query=truck%20dispatcher&location=' + zip + '&radiusInMiles=20&num=100&start=' + str(page * 100) + '&userguid=c0111cda-a2f4-40af-985a-9d88fc29404a&suppressViewLocations=false&searchFrameId=28ade9b0-ffe8-461b-a2f1-7cf3b86c3300&searchFocusId=17e75b4b-815a-47fc-a0ed-f1dc586d5600&searchRequestId=5ea0c321-34e2-4c80-ad8f-8509c3b1addd&includeJobDescriptions=true&includeFilterGroups=category&includeFilterGroups=industry&includeFilterGroups=features&includeFilterGroups=experiencelevel&includeFilterGroups=shifts&includeFilterGroups=urgentlyhiring&includeFilterGroups=instantinterview&includeFilterGroups=normalizedbrandname&includeFilterGroups=easyapply'

ziplist = ['10001', '10002', '10005', '11101', '10003', '20001', '23220', '33101', '11201', '10011', '10025', '32210', '30303', '33311', '21215', '30004', '30331', '10023', '20011', '11212', '10004', '30040', '11220', '11234', '11221', '30024', '11211', '10010', '33023', '20002', '33125', '21224', '30022', '10013', '21043', '32244', '10022', '43215', '30305', '02124', '33142', '33411', '11203', '21230', '33024', '11434', '30044', '11432', '30342', '45011', '10021', '21234', '11235', '20110', '10024', '23454', '10451', '30135', '10314', '33132', '33025', '10453', '33312', '30324', '30310', '23320', '30043', '11233', '11040', '11215', '44102', '11213', '10012', '22030', '33313', '33012', '11222', '33134', '11204', '10014', '21213', '33155', '15212', '11550', '44130', '02301', '22304', '33021', '02155', '33401', '78256', '66030', '05753', '37917', '77539', '78728', '94536', '83844', '99328', '97224', '61341', '15233', '74701', '11704', '79201', '08050', '61469', '23666', '06405', '27330', '11795', '92123', '77026', '94590', '33313', '97701', '30552']

class SnagaJobSpider(scrapy.Spider):
    name = 'snagajob'

    def start_requests(self):
        for zip in ziplist:
            yield JsonRequest(
                url=get_url(0, zip),
                method='GET',
                dont_filter=True,
                callback=self.parse_page,
                cb_kwargs={'zip':zip, 'page': 0})

    def parse_page(self, response, zip, page):
        jobs = response.json().get('list')

        for item in jobs:
            items = MultyItem()

            source_id = item.get('postingId')
            position = item.get('title')
            link = item.get('applicationUrl')

            company = item.get('companyName')
            logo_url = item.get('logoUrl')

            location = item.get('location').get('locationName')

            salary = ''
            if item.get('estimatedWage') is not None:
                salary = item.get('estimatedWage').get('text')

            schedule = ' | '.join([i for i in item.get('categories')])

            shift = ''

            short_description = item.get('jobDescription')
            full_description = item.get('jobDescription')

            items['source_id'] = source_id
            items['position'] = position
            items['company'] = company
            items['location'] = location
            items['salary'] = salary
            items['schedule'] = schedule
            items['shift'] = shift
            items['short_description'] = short_description
            items['full_description'] = full_description
            items['link'] = link
            items['website'] = self.name
            items['logo_url'] = logo_url
            items['created_at'] = datetime.now()

            yield items

        if (page * 100) < 500:
            yield JsonRequest(
                url=get_url(page+1, zip),
                method='GET',
                dont_filter=True,
                callback=self.parse_page,
                cb_kwargs={'zip':zip, 'page': page+1})