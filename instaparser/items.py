# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    username = scrapy.Field()
    gen_user = scrapy.Field()
    user_id = scrapy.Field()
    photo = scrapy.Field()
    likes = scrapy.Field()
    post_data = scrapy.Field()
    _id = scrapy.Field()




