# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies

    def process_item(self, item, spider):
        collection = self.mongobase['vc_all']
        collection.insert_one(dict(item))

        return item

    def process_salary(self, salary):
        return None, None, None
