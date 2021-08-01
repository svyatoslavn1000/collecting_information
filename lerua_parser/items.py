# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose


def prepare_data(value):
    price = int(value.replace(' ', ''))
    return price


def prepare_image(value):
    try:
        photos = value.replace('w_82,h_82', 'w_1200,h_1200')
        return photos
    except Exception as e:
        print(e)


def prepare_specifications(value):
    specifications_list = value.xpath('..//div')
    result_specifications = {}
    for item in specifications_list:
        specifications_name = item.xpath('.//dt/text()').extract()[0]
        specifications_value = item.xpath('.//dd/text()').extract()[0].replace('\n', '').strip()
        result_specifications[specifications_name] = specifications_value
    return result_specifications


class LeruaParserItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(prepare_data))
    article = scrapy.Field()
    text = scrapy.Field()
    photos = scrapy.Field(input_processor=MapCompose(prepare_image))
    specifications = scrapy.Field(
        input_processor=MapCompose(prepare_specifications))
    _id = scrapy.Field()