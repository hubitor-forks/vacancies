LOG_STDOUT = True
LOG_FILE = 'log.txt'
LOG_LEVEL = 'INFO'

USER_AGENT= 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0',

# ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'pipelines.MultyPipeline': 300,
}

# scrapy-playwright
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# PLAYWRIGHT_LAUNCH_OPTIONS = {
# 	"headless": False,
# 	"slow_mo": 50,
# 	# "proxy": { "server": "http://192.168.1.19:8889" },
# }

PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 200000
PLAYWRIGHT_ABORT_REQUEST = lambda req: req.resource_type == "image"
PLAYWRIGHT_MAX_PAGES_PER_CONTEXT = 1