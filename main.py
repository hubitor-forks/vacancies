from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from spiders.monster import MonsterSpider
from spiders.simplyhired import SimplyHiredSpider
from spiders.careerbuilder import CareerBuilderSpider
from spiders.glassdoor import GlassDoorSpider
from spiders.jobtoday import JobtodaySpider
from spiders.jobsinlogistics import JobsInLogisticsSpider
from spiders.jooble import JoobleSpider

from spiders.ararentalworksspider import ArarentalWorksSpider
from spiders.kehespider import KeheSpider
from spiders.linkedinspider import LinkedInSpider
from spiders.workuaspider import WorkUaSpider
from spiders.salaryspider import SalarySpider
from spiders.jobstreetspider import JobStreetSpider
from spiders.snagajobspider import SnagaJobSpider
from spiders.seekspider import SeekSpider


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    # # First
    # process.crawl(JobsInLogisticsSpider)
    process.crawl(SimplyHiredSpider)
    process.crawl(MonsterSpider)          #<+++++
    process.crawl(CareerBuilderSpider)
    process.crawl(GlassDoorSpider)
    process.crawl(JoobleSpider)    #<++++++
    process.crawl(JobtodaySpider)

    # # Seccond
    process.crawl(KeheSpider)
    process.crawl(LinkedInSpider)
    process.crawl(WorkUaSpider)
    process.crawl(SalarySpider)
    process.crawl(JobStreetSpider)
    process.crawl(SnagaJobSpider)
    process.crawl(SeekSpider)

    process.start()
