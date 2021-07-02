from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from jobparser import settings
from jobparser.spiders.hh_ru import HhRuSpider
from jobparser.spiders.superjob import SuperjobSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhRuSpider)
    process.crawl(SuperjobSpider)

    process.start()
