from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from lerua_parser import settings
from lerua_parser.spiders.leroy_merlin import LeroyMerlinSpider

if __name__ == '__main__':
    searchInput = 'Газовые нагреватели'

    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(LeroyMerlinSpider, searchInput=searchInput)
    process.start()