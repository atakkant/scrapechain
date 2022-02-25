# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch, helpers
import types
from datetime import datetime



class ElasticsearchPipeline:
    def __init__(self):
        self.client = Elasticsearch("http://localhost:9200")
        self.buffer = []
        self.buffer_length = 5



    def create_unique_id(self,item,key):
        unique_key = item.get(key)
        if unique_key:
            return unique_key
        else:
            return False

    def index_item(self,item,spider):
        unique_id = self.create_unique_id(item,spider.unique_key)
        index_name = spider.name
        type = spider.type_name
        index_action = {
            '_index':index_name,
            '_id': unique_id,
            '_type': type,
            '_source': dict(item)
        }
        print('index action created with unique_id: %s'%unique_id)

        self.buffer.append(index_action)
        if len(self.buffer) >= self.buffer_length:
            self.send_items()
            self.buffer = []

    def send_items(self):
        helpers.bulk(self.client,self.buffer)

    def process_item(self, item, spider):
        print("processing elastticsearch")
        resp = self.client.info()
        print(resp)
        item["time"] = datetime.now()
        if isinstance(item,types.GeneratorType) or isinstance(item,list):
            for each in item:
                self.process_item(each,spider)
        else:
            self.index_item(item,spider)
            print("item sent to Elastic Search %s"%item.get(spider.unique_key))

        return item

    def close_spider(self,spider):
        if len(self.buffer):
            self.send_items()
