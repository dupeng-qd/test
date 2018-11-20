# -*- coding: utf-8 -*-

import scrapy

from zz_spiders import env
from zz_spiders.service.user_shop import UserShop
from zz_spiders.items import DailyShopList
from zz_spiders.items import UsersShopsList
from zz_spiders.utils.mongoDB import Mongodb
import json
import datetime

class CheckShopsStatus(scrapy.Spider):

    name = "check_shops_status"  #获取直通车服务中的店铺

    custom_settings = {
        'ITEM_PIPELINES': {
            'zz_spiders.pipelines.AddDateTimePipeline': 300,
            'zz_spiders.pipelines.SaveDataToMongodb': 400,
        },
    }
    shops = []
    save_shops = {}
    total_count = 0
    parse_count = 0

    mongodb_collection = ""


    def del_today_data(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        client = Mongodb('daily_shops_list', 'zz_web')

        result = client.delete_many({
                    "created_at": {'$gte': today+' 00:00:00','$lte': today+' 23:59:59'}
                })

        client = Mongodb('users_shops_list', 'zz_web')

        result = client.delete_many({
            "created_at": {'$gte': today+' 00:00:00','$lte': today+' 23:59:59'}
        })

    def generate_requests(self):
        result = []
        self.shops = UserShop().get()
        # 店铺去重
        shops = []
        for shop in self.shops:
            shops.append(shop['shop_name'])
        shops = set(shops)

        for shop in shops:
            zhitongche_request = scrapy.Request(
                url=env.api_zhitongche_url+'/sdk.check.php?shopName='+shop,
                callback=self.parse,
                errback=self.errback
            )
            zuanzhan_request = scrapy.Request(
                url=env.api_zuanzhan_url+'/sdk.check.php?shopName=' + shop,
                callback=self.parse,
                errback=self.errback
            )

            zhitongche_request.meta['shop'] = shop
            zhitongche_request.meta['type'] = "zhitongche"
            zuanzhan_request.meta['shop'] = shop
            zuanzhan_request.meta['type'] = "zuanzhan"

            result.append(zhitongche_request)
            result.append(zuanzhan_request)

        self.total_count = len(result)

        return result

    # 获取
    def start_requests(self):
        self.del_today_data()
        requests = self.generate_requests()
        for request in requests:
            yield request

    def errback(self):
        self.parse_count += 1
        self.total_count += 1

        if self.total_count == self.parse_count:
            save_data = self.save_data()

            self.mongodb_collection = "daily_shops_list"
            yield DailyShopList(data=save_data['daily_shops_list'])

            self.mongodb_collection = "users_shops_list"
            for user in save_data['users_shops_list']:
                yield UsersShopsList(data=user)

    def parse(self, response):
        self.parse_count += 1
        res = json.loads(response.text)
        if res['status'] == "succ":
            if response.meta['shop'] not in self.save_shops:
                self.save_shops[response.meta['shop']] = {}

            if response.meta['type'] == "zhitongche":
                self.save_shops[response.meta['shop']]["zhitongche_status"] = res['data']
            if response.meta['type'] == "zuanzhan":
                self.save_shops[response.meta['shop']]["zuanzhan_status"] = res['data']


            if self.total_count == self.parse_count:

                save_data = self.save_data()

                self.mongodb_collection = "daily_shops_list"
                yield DailyShopList(data=save_data['daily_shops_list'])

                self.mongodb_collection = "users_shops_list"
                for user in save_data['users_shops_list']:
                    yield UsersShopsList(data=user)


    def save_data(self):

        daily_shops_list = []
        users_shops_list = self.shops

        # 生成店铺列表
        for shop in self.save_shops:
            daily_shops_list.append(
                {
                    'shop_name': shop,
                    'zhitongche_status': self.save_shops[shop]['zhitongche_status'],
                    'zuanzhan_status': self.save_shops[shop]['zuanzhan_status'],
                }
            )

        # 生成用户列表
        for user in users_shops_list:
            user['zhitongche_status'] = self.save_shops[user['shop_name']]['zhitongche_status']
            user['zuanzhan_status'] = self.save_shops[user['shop_name']]['zuanzhan_status']


        return {
            'daily_shops_list': daily_shops_list,
            'users_shops_list': users_shops_list,
        }


