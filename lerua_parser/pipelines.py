from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient
import hashlib
import json


class LeroyParserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client['lerua']

    def process_item(self, item, spider):
        collection_name = 'lerua'
        try:
            collection = self.db.create_collection(f'{collection_name}')
        except:
            collection = self.db[collection_name]

        item_mongo = json.dumps(dict(item)).encode('utf-8')
        hash = hashlib.sha3_512(item_mongo)
        id = hash.hexdigest()
        item['_id'] = id

        try:
            collection.insert_one(item)

        except Exception as e:
           print(e)

        return item


class LeroyImagesLoader(ImagesPipeline):

    def get_media_requests(self, item, info):
        photo = item['photos']
        if photo:
            for img in photo:
                try:
                    yield scrapy.Request(img)

                except Exception as e:
                    print(e)

    def file_path(self, request, response=None, info=None, *, item=None):
        directory_name = item['name'][0].replace('/', '_')
        file_name = request.url.split('/')[-1]
        return f'{directory_name}/{file_name}'

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item