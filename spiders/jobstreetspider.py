import scrapy
from scrapy.http.request.json_request import JsonRequest
import w3lib.html

from items import MultyItem
from datetime import datetime


headers = {
    'Accept': '*/*',
    'Origin': 'https://www.jobstreet.com.ph',
    'Accept-Language': 'ru',
    'Host': 'www.jobstreet.com.ph',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.1 Safari/605.1.15',
    'Referer': 'https://www.jobstreet.com.ph/en/job-search/truck-dispatcher-jobs/?createdAt=1d&salary=0&salary-max=2147483647',
    'Connection': 'keep-alive',
}

def get_data(page):
    return {
        'query': 'query getJobs($country: String, $locale: String, $keyword: String, $createdAt: String, $jobFunctions: [Int], $categories: [String], $locations: [Int], $careerLevels: [Int], $minSalary: Int, $maxSalary: Int, $salaryType: Int, $candidateSalary: Int, $candidateSalaryCurrency: String, $datePosted: Int, $jobTypes: [Int], $workTypes: [String], $industries: [Int], $page: Int, $pageSize: Int, $companyId: String, $advertiserId: String, $userAgent: String, $accNums: Int, $subAccount: Int, $minEdu: Int, $maxEdu: Int, $edus: [Int], $minExp: Int, $maxExp: Int, $seo: String, $searchFields: String, $candidateId: ID, $isDesktop: Boolean, $isCompanySearch: Boolean, $sort: String, $sVi: String, $duplicates: String, $flight: String, $solVisitorId: String) {\n  jobs(\n    country: $country\n    locale: $locale\n    keyword: $keyword\n    createdAt: $createdAt\n    jobFunctions: $jobFunctions\n    categories: $categories\n    locations: $locations\n    careerLevels: $careerLevels\n    minSalary: $minSalary\n    maxSalary: $maxSalary\n    salaryType: $salaryType\n    candidateSalary: $candidateSalary\n    candidateSalaryCurrency: $candidateSalaryCurrency\n    datePosted: $datePosted\n    jobTypes: $jobTypes\n    workTypes: $workTypes\n    industries: $industries\n    page: $page\n    pageSize: $pageSize\n    companyId: $companyId\n    advertiserId: $advertiserId\n    userAgent: $userAgent\n    accNums: $accNums\n    subAccount: $subAccount\n    minEdu: $minEdu\n    edus: $edus\n    maxEdu: $maxEdu\n    minExp: $minExp\n    maxExp: $maxExp\n    seo: $seo\n    searchFields: $searchFields\n    candidateId: $candidateId\n    isDesktop: $isDesktop\n    isCompanySearch: $isCompanySearch\n    sort: $sort\n    sVi: $sVi\n    duplicates: $duplicates\n    flight: $flight\n    solVisitorId: $solVisitorId\n  ) {\n    total\n    totalJobs\n    relatedSearchKeywords {\n      keywords\n      type\n      totalJobs\n    }\n    solMetadata\n    suggestedEmployer {\n      name\n      totalJobs\n    }\n    queryParameters {\n      key\n      searchFields\n      pageSize\n    }\n    experiments {\n      flight\n    }\n    jobs {\n      id\n      adType\n      sourceCountryCode\n      isStandout\n      companyMeta {\n        id\n        advertiserId\n        isPrivate\n        name\n        logoUrl\n        slug\n      }\n      jobTitle\n      jobUrl\n      jobTitleSlug\n      description\n      employmentTypes {\n        code\n        name\n      }\n      sellingPoints\n      locations {\n        code\n        name\n        slug\n        children {\n          code\n          name\n          slug\n        }\n      }\n      categories {\n        code\n        name\n        children {\n          code\n          name\n        }\n      }\n      postingDuration\n      postedAt\n      salaryRange {\n        currency\n        max\n        min\n        period\n        term\n      }\n      salaryVisible\n      bannerUrl\n      isClassified\n      solMetadata\n    }\n  }\n}\n',
        'variables': {
            'keyword': 'truck dispatcher',
            'jobFunctions': [],
            'locations': [],
            'salaryType': 1,
            'maxSalary': 2147483647,
            'jobTypes': [],
            'createdAt': '1d',
            'careerLevels': [],
            'page': page,
            'country': 'ph',
            'sVi': '',
            'solVisitorId': '3223e5d0-e9ba-4bed-af77-ed34a0560917',
            'categories': [],
            'workTypes': [],
            'userAgent': 'Mozilla/5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/605.1.15%20(KHTML,%20like%20Gecko)%20Version/15.6.1%20Safari/605.1.15',
            'industries': [],
            'locale': 'en',
        },
    }

class JobStreetSpider(scrapy.Spider):
    name = 'jobstreet'

    curr_page = 1

    def start_requests(self):
        yield JsonRequest(
            url='https://www.jobstreet.com.ph/job-search/graphql?country=ph&isSmartSearch=true',
            method='POST',
            dont_filter=True,
            headers=headers,
            data=get_data(self.curr_page),
            callback=self.parse_page)

    def parse_page(self, response):
        jobs = response.json().get('data').get('jobs').get('jobs')

        for job in jobs:
            items = MultyItem()

            source_id = job.get('id')
            position = job.get('jobTitle')
            link = job.get('jobUrl')

            company = job.get('companyMeta').get('name')
            logo_url = job.get('companyMeta').get('logoUrl')

            location = job.get('locations')[0].get('name')

            salary_min = job.get('salaryRange').get('min')
            salary_max = job.get('salaryRange').get('max')
            salary_period = job.get('salaryRange').get('period')

            salary = ''

            if salary_min is not None or salary_max is not None:
                salary = str(salary_min) + ' - ' + str(salary_max) + ' ' + salary_period

            schedule = ' | '.join([i.get('name') for i in job.get('employmentTypes')])

            shift = ''

            short_description = job.get('description')
            full_description = job.get('description')

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

        if len(jobs) > 0:
            self.curr_page += 1
            yield JsonRequest(
            url='https://www.jobstreet.com.ph/job-search/graphql?country=ph&isSmartSearch=true',
            method='POST',
            dont_filter=True,
            headers=headers,
            data=get_data(self.curr_page),
            callback=self.parse_page)