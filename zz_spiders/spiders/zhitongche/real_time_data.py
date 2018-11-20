# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/10/24
   File Name：     real_time_data
   Description:     店铺实时数据
-------------------------------------------------
"""

import scrapy
import json
from zz_spiders import env
from zz_spiders.service.get_shop_list import get_shops_list
from zz_spiders.items import ZTCRealTimeDateItem
import datetime
from zz_spiders.utils.redis import RedisDatabase


class RealTimeData(scrapy.Spider):
    name = 'zhitongche.real_time_data'
    custom_settings = {
        'ITEM_PIPELINES': {
            'zz_spiders.pipelines.SaveShopDataToRedis': 400,
        },

    }
    shop_list = None

    def __init__(self, begin, end, *args, **kwargs):
        shop_list = get_shops_list()
        self.shop_list = shop_list[int(begin):int(end)]

    def start_requests(self):
        curr_hour = datetime.datetime.now().hour
        url_real_time = env.api_zhitongche_url + '/sdk.single.php?shopName={0}'

        hour = datetime.datetime.now() - datetime.timedelta(hours=1)       # 构造redis key 的时间，当前时间-1
        hour = hour.strftime('%H')

        real_time_date = datetime.datetime.now().strftime('%Y%m%d')   # 构造redis 实时数据key 的日期

        yesterday = datetime.date.today() - datetime.timedelta(days=1)  # 构造redis 历史数据key 的日期
        history_time_date = yesterday.strftime('%Y%m%d')

        for i in self.shop_list:
            shopname = i['shop_name']
            if curr_hour == 5:
                yesterday = datetime.date.today() - datetime.timedelta(days=1)
                yesterday = yesterday.strftime('%Y-%m-%d')
                url_history_time = env.api_zhitongche_url + '/sdk.single.php?shopName={0}&date=' + yesterday

                request_history_time = scrapy.Request(url=url_history_time.format(i['shop_name']), callback=self.parse)
                request_real_time = scrapy.Request(url=url_real_time.format(i['shop_name']), callback=self.parse)

                request_history_time.meta['shopname'] = shopname
                request_real_time.meta['shopname'] = shopname

                request_history_time.meta['redis_date'] = history_time_date
                request_real_time.meta['redis_date'] = real_time_date

                request_history_time.meta['hour'] = 23
                request_real_time.meta['hour'] = hour

                yield request_history_time
                yield request_real_time
            else:
                request = scrapy.Request(url=url_real_time.format(i['shop_name']), callback=self.parse)
                request.meta['shopname'] = shopname
                request.meta['hour'] = hour
                request.meta['redis_date'] = real_time_date
                yield request

    def parse(self, response):
        resp = json.loads(response.text)
        shopname = response.meta['shopname']
        if resp['status'] == 'succ':
            yield ZTCRealTimeDateItem(
                shopdata=json.dumps(resp['data']),
                shopname=shopname,
                hour=response.meta['hour'],
                redis_date=response.meta['redis_date']
            )

        curr_hour = datetime.datetime.now().hour
        if curr_hour == 6:
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            yesterday = yesterday.strftime('%Y%m%d')
            key_7 = 'shop_data:{}:{}:{}'.format(shopname, yesterday, '07')
            key_15 = 'shop_data:{}:{}:{}'.format(shopname, yesterday, '15')
            key_23 = 'shop_data:{}:{}:{}'.format(shopname, yesterday, '23')

            r_client = RedisDatabase()

            cost_7 = 0
            percent_7 = 0
            percent_15 = 0
            cost_15_all = 0

            # 如果计划在7/15点之前暂停，但在这一天是有推广时间段的
            key_7_list = ['06', '05', '04', '03', '02', '01', '00']
            key_15_list = ['14', '13', '12', '11', '10', '09', '08']

            if r_client.exists(key_15):     # 取15时的花费数据
                data_15 = r_client.get_data(key_15)
                cost_15_all = float(json.loads(data_15)['cost'])

            if r_client.exists(key_23):     # 取23时的花费数据
                data_all = r_client.get_data(key_23)
                cost_all = float(json.loads(data_all)['cost'])

                if (cost_all - cost_15_all) < 0:    # 如果 23时 的数据小于 15 时的数据，用22 时的数据计算进度条
                    key_22 = 'shop_data:{}:{}:{}'.format(shopname, yesterday, '22')
                    data_all = r_client.get_data(key_22)
                    cost_all = float(json.loads(data_all)['cost'])

                if cost_all != 0:
                    if r_client.exists(key_7):      # 计算7点的花费，进而求7点的花费占比
                        data_7 = r_client.get_data(key_7)
                        cost_7 = float(json.loads(data_7)['cost'])
                        percent_7 = '{:.2f}'.format(100 * cost_7/cost_all)
                    else:
                        for i in key_7_list:
                            key = 'shop_data:{}:{}:{}'.format(shopname, yesterday, i)
                            if r_client.exists(key):
                                data_7 = r_client.get_data(key)
                                cost_7 = float(json.loads(data_7)['cost'])
                                percent_7 = '{:.2f}'.format(100 * cost_7 / cost_all)
                                break

                    if r_client.exists(key_15):     # 计算15时的花费，求15点的花费占比
                        data_15 = r_client.get_data(key_15)
                        cost_15_all = float(json.loads(data_15)['cost'])
                        cost_15 = cost_15_all - cost_7
                        percent_15 = '{:.2f}'.format(100 * cost_15/cost_all)
                    else:
                        for i in key_15_list:
                            key = 'shop_data:{}:{}:{}'.format(shopname, yesterday, i)
                            if r_client.exists(key):
                                data_15 = r_client.get_data(key)
                                cost_15_all = float(json.loads(data_15)['cost'])
                                cost_15 = cost_15_all - cost_7
                                percent_15 = '{:.2f}'.format(100 * cost_15 / cost_all)
                                break
                            else:
                                cost_15_all = cost_7    # 8-16之间没数据，当前总数据即 八点的总数据

                    percent_23 = '{:.2f}'.format(100 * (cost_all-cost_15_all)/cost_all)     # 23时的花费占比

                    percent = [percent_7, percent_15, percent_23]   # 进度条
                    percent = json.dumps(percent)

                    key = 'shop_percent:{}:{}'.format(shopname, yesterday)
                    r_client.save_data(key, percent)
