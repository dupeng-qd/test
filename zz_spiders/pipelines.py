# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
from .utils.mongoDB import Mongodb
from zz_spiders.utils.data import Data
from zz_spiders.spiders.zhitongche.shop.shop_information import ShopInformation
from zz_spiders.spiders.zhitongche.shop.shop_history_data_handle import ShopHistoryDataHandle
from zz_spiders.utils.redis import RedisDatabase
from zz_spiders.utils.date import Date
import re


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


class SaveShopDataToMysql(object):
    def process_item(self, item, spider):
        table = item['table']
        key = item['key']
        value = item['value']
        if 'f_nick' in key:
            key.append('created_at')
            value.append(item['created_at'])

            key.append('updated_at')
            value.append(item['updated_at'])
        else:
            key.append('f_nick')
            value.append(item['shopname'])

        Data().mysql_column(table, key, value)

    def close_spider(self, spider):
        if spider.name == 'zhitongche.shop.shop_history_data':
            ShopInformation().get_shop_name()


class SaveShopHistoryDataToMongodb(object):
    def process_item(self, item, spider):
        print(item['shopname'], item['status'], item['data'])
        if item['status'] == 1:
            client = Mongodb('zhitongche_history_data', 'zz_web')
        else:
            client = Mongodb('zuanzhan_history_data', 'zz_web')

        client.save_data(item)
        client.close()

    def open_spider(self, spider):
        client = Mongodb('zhitongche_history_data', 'zz_web')
        client.delete_many({
            "created_at": {'$gte': Date().get_today() + ' 00:00:00', '$lte': Date().get_today() + ' 23:59:59'}
        })
        client = Mongodb('zuanzhan_history_data', 'zz_web')
        client.delete_many({
            "created_at": {'$gte': Date().get_today() + ' 00:00:00', '$lte': Date().get_today() + ' 23:59:59'}
        })

    def close_spider(self, spider):
        if spider.name == 'zhitongche.shop.shop_history_data':
            ShopHistoryDataHandle().handle_main()
            # ShopInformation().get_shop_name()


# if __name__ == "__main__":
#     SaveShopDataToMysql().mysql_column('t_shop_data', ['f_cpc'], ['aa'])
