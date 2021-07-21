import os

if os.path.isfile("config/+79161230219_uuid_and_cookie.json"):
    os.remove("config/+79161230219_uuid_and_cookie.json")

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instaparser.spiders.instagram import InstagramSpider
from instaparser import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider)

    process.start()