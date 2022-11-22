import scrapy


class MultyItem(scrapy.Item):
    source_id = scrapy.Field()
    position = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    salary = scrapy.Field()
    schedule = scrapy.Field()
    shift = scrapy.Field()
    short_description = scrapy.Field()
    full_description = scrapy.Field()
    link = scrapy.Field()
    website = scrapy.Field()
    logo_url = scrapy.Field()
    updated_at = scrapy.Field()
    created_at = scrapy.Field()
