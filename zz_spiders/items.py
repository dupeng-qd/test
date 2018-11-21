# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseItem(scrapy.Item):
    created_at = scrapy.Field()
    updated_at = scrapy.Field()
    pass


class DailyShopList(BaseItem):
    data = scrapy.Field()
    pass

class UsersShopsList(BaseItem):
    data = scrapy.Field()
    pass


class ZTCRealTimeDateItem(scrapy.Item):
    shopdata = scrapy.Field()
    shopname = scrapy.Field()
    hour = scrapy.Field()
    redis_date = scrapy.Field()
    pass


class ZTCCampaignRealTimeDataItem(scrapy.Item):
    shopdata = scrapy.Field()
    shopname = scrapy.Field()
    hour = scrapy.Field()
    redis_date = scrapy.Field()
    pass


class ZTCShopHistoryDataItem(BaseItem):
    shopname = scrapy.Field()
    table = scrapy.Field()
    key = scrapy.Field()
    value = scrapy.Field()
    pass


class ShopHistoryDataItem(BaseItem):
    status = scrapy.Field()
    budget = scrapy.Field()
    shopname = scrapy.Field()
    data = scrapy.Field()
