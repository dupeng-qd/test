# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/11/12
   File Name：     shop_history_data
   Description:
-------------------------------------------------
"""

import scrapy
import json
from zz_spiders import env
from zz_spiders.service.get_shop_list import get_shops_list
from zz_spiders.items import ZTCShopHistoryDataItem
import datetime
from zz_spiders.utils.data import Data
import requests


class ShopHistoryData(scrapy.Spider):
    name = 'zhitongche.shop.shop_history_data'
    custom_settings = {
        'ITEM_PIPELINES': {
            'zz_spiders.pipelines.SaveShopDataToMysql': 400,
            'zz_spiders.pipelines.AddDateTimePipeline': 300,
        },
    }
    shop_list = None

    def __init__(self, begin, end, *args, **kwargs):
        self.shop_list = get_shops_list(flag='all')
        # self.shop_list = shop_list[int(begin):int(end)]

    def start_requests(self):
        for i in self.shop_list:
            shopname = i['shop_name']
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            yesterday = yesterday.strftime('%Y-%m-%d')
            url_history_time = ''
            url_budget = ''
            if i['zhitongche_status'] == 0 and i['zuanzhan_status'] == 0:   # 如果是没有授权的店铺，跳过
                continue
            elif i['zhitongche_status'] == 1:
                url_history_time = env.api_zhitongche_url + '/sdk.single.php?shopName={0}&date=' + yesterday
                url_budget = env.api_zhitongche_url + '/sdk.budget.php?shopName={}'
            elif i['zuanzhan_status'] == 1:
                url_history_time = env.api_zuanzhan_url + '/sdk.single.php?shopName={0}&date=' + yesterday
                url_budget = env.api_zuanzhan_url + '/sdk.budget.php?shopName={}'

            resp = requests.get(url_budget.format(shopname))
            budget = resp.json()['data']
            if budget:
                budget = budget['budget']

            request_history_time = scrapy.Request(url=url_history_time.format(shopname), callback=self.parse)
            request_history_time.meta['shopname'] = shopname
            request_history_time.meta['budget'] = budget
            yield request_history_time

    def parse(self, response):
        resp = json.loads(response.text)
        if resp['status'] == 'succ':
            shopname = response.meta['shopname']
            budget = response.meta['budget']
            key = []
            value = []
            data = resp['data']
            if budget:
                key.append('f_budget')
                value.append(budget)
            for i in data:
                value.append(data[i])
                i = 'f_' + i
                key.append(i)

            yield ZTCShopHistoryDataItem(
                shopname=shopname,
                table='t_shop_data',
                key=key,
                value=value
            )
