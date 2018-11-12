# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
from .utils.mongoDB import Mongodb

from zz_spiders.utils.redis import RedisDatabase

class AddDateTimePipeline(object):

    def process_item(self, item, spider):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item["created_at"] = now
        item["updated_at"] = now

        return item


class SaveShopDataToRedis(object):
    def process_item(self, item, spider):
        r = RedisDatabase()
        key = 'shop_data:{0}:{1}:{2}'.format(item['shopname'], item['redis_date'], item['hour'])
        r.save_data(key, item['shopdata'])


class SaveCampaignDataToRedis(object):
    def process_item(self, item, spider):
        r = RedisDatabase()
        for campaign in item['shopdata']:
            key = 'campaign_data:{0}:{1}:{2}:{3}'.format(item['shopname'], campaign, item['redis_date'], item['hour'])
            r.save_data(key, item['shopdata'][campaign])


class SaveDataToMongodb(object):

    client = None
    def process_item(self, item, spider):

        self.client = Mongodb(spider.mongodb_collection, 'zz_web')
        self.client.save_data(item)
        self.client.close()
