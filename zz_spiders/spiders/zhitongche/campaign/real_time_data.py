# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/11/5
   File Name：     real_name_data
   Description:     计划的实时数据
-------------------------------------------------
"""

import scrapy
import json
from zz_spiders import env
from zz_spiders.service.get_shop_list import get_shops_list
from zz_spiders.items import ZTCCampaignRealTimeDataItem
from zz_spiders.utils.redis import RedisDatabase
import datetime


class RealTimeData(scrapy.Spider):
    name = 'zhitongche.campaign.real_time_data'
    custom_settings = {
        'ITEM_PIPELINES': {
            'zz_spiders.pipelines.SaveCampaignDataToRedis': 400,
        },

    }
    shop_list = None

    def __init__(self, begin, end, *args, **kwargs):
        shop_list = get_shops_list()
        self.shop_list = shop_list[int(begin):int(end)]

    def start_requests(self):
        curr_hour = datetime.datetime.now().hour  # 当前执行爬虫的时间
        url_real_time = env.api_zhitongche_url + '/sdk.campaign_rtrpt.php?shopName={0}'

        hour = datetime.datetime.now() - datetime.timedelta(hours=1)       # 构造redis key 的时间，当前时间-1
        hour = hour.strftime('%H')

        real_time_date = datetime.datetime.now().strftime('%Y%m%d')   # 构造redis 实时数据key 的日期

        yesterday = datetime.date.today() - datetime.timedelta(days=1)  # 构造redis 历史数据key 的日期
        history_time_date = yesterday.strftime('%Y%m%d')

        for i in self.shop_list:
            shopname = i['shop_name']
            if curr_hour == 4:
                yesterday = datetime.date.today() - datetime.timedelta(days=1)
                yesterday = yesterday.strftime('%Y-%m-%d')
                url_history_time = env.api_zhitongche_url + '/sdk.campaign_rtrpt.php?shopName={0}&date=' + yesterday

                request_history_time = scrapy.Request(url=url_history_time.format(i['shop_name']), callback=self.parse)
                request_real_time = scrapy.Request(url=url_real_time.format(i['shop_name']), callback=self.parse)

                request_history_time.meta['shopname'] = shopname
                request_real_time.meta['shopname'] = shopname

                request_history_time.meta['redis_date'] = history_time_date
                request_real_time.meta['redis_date'] = real_time_date

                request_history_time.meta['hour'] = 23
                request_real_time.meta['hour'] = hour

                yield request_real_time
                yield request_history_time
            else:
                request = scrapy.Request(url=url_real_time.format(i['shop_name']), callback=self.parse)
                request.meta['shopname'] = shopname
                request.meta['hour'] = hour
                request.meta['redis_date'] = real_time_date
                yield request

    def parse(self, response):
        resp = json.loads(response.text)
        shopname = response.meta['shopname']
        campaign_list = {}
        for campaign in resp['data']:
            campaign_id = campaign['campaignid']

            if campaign_id not in campaign_list:
                campaign_list[campaign_id] = campaign
            else:
                campaign_list[campaign_id] = dict(campaign_list[campaign_id], **campaign)

        if resp['status'] == 'succ':
            yield ZTCCampaignRealTimeDataItem(
                shopdata=campaign_list,
                shopname=shopname,
                hour=response.meta['hour'],
                redis_date=response.meta['redis_date']
                # campaign=campaign_list
            )

        curr_hour = datetime.datetime.now().hour
        if curr_hour == 4:
            for cam in campaign_list:
                yesterday = datetime.date.today() - datetime.timedelta(days=1)
                yesterday = yesterday.strftime('%Y%m%d')
                key_7 = 'campaign_data:{}:{}:{}:{}'.format(shopname, cam, yesterday, '07')
                key_15 = 'campaign_data:{}:{}:{}:{}'.format(shopname, cam, yesterday, '15')
                key_23 = 'campaign_data:{}:{}:{}:{}'.format(shopname, cam, yesterday, '23')

                r_client = RedisDatabase()

                if r_client.exists(key_23):
                    data_all = r_client.get_data(key_23)
                    cost_all = json.loads(data_all.replace('\'', '"'))
                    cost_all = float(cost_all['cost'])

                    if cost_all == 0:
                        continue

                    # if r_client.exists(key_7):
                    data_7 = r_client.get_data(key_7)
                    cost_7 = json.loads(data_7.replace('\'', '"'))
                    cost_7 = float(cost_7['cost'])
                    percent_7 = '{:.2f}'.format(100 * cost_7 / cost_all)
                    key = 'campaign_percent:{}:{}:{}'.format(shopname, cam, yesterday)

                    # if r_client.exists(key_15):
                    data_15 = r_client.get_data(key_15)
                    cost_15_all = json.loads(data_15.replace('\'', '"'))
                    cost_15_all = float(cost_15_all['cost'])
                    cost_15 = cost_15_all - cost_7
                    percent_15 = '{:.2f}'.format(100 * cost_15 / cost_all)

                    percent_23 = '{:.2f}'.format(100 * (cost_all - cost_15_all) / cost_all)

                    percent = [percent_7, percent_15, percent_23]
                    percent = json.dumps(percent)

                    r_client.save_data(key, percent)
