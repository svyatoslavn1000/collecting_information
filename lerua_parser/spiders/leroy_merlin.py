import scrapy
from scrapy.loader import ItemLoader
from lerua_parser.items import LeruaParserItem


class LeroyMerlinSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['leroymerlin.ru']
    url = 'https://leroymerlin.ru'

    def __init__(self, searchInput):
        super(LeroyMerlinSpider, self).__init__()
        self.search  = searchInput
        self.start_urls = [self.url + f'/search/?q={self.search}&suggest=true']

    def parse(self, response):
        product_links = response.xpath('//a[@data-qa="product-name"]/@href').extract()
        for link in product_links:
            yield response.follow(f'{self.url + link}', callback=self.parse_goods)

        next_link = response.xpath('//a[contains(@aria-label, "Следующая страница")]/@href').extract()
        if next_link[0] != None:
            next_page = self.url + next_link[0]
            yield response.follow(next_page, callback=self.parse)

    def parse_goods(self, response):
        loader = ItemLoader(item=LeruaParserItem(), response=response)
        loader.add_xpath('name', '//h1/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('price', '//span[@slot="price"]/text()')
        loader.add_xpath('article', '//span[@slot="article"]/text()')
        loader.add_xpath('text', '//uc-pdp-section-layout/uc-pdp-section-vlimited/div/p/text()')
        loader.add_xpath('photos', '//img[@alt="image thumb"]/@src')
        specifications_list = response.xpath('//dl[@class="def-list"]')
        loader.add_value('specifications', specifications_list)

        yield loader.load_item()