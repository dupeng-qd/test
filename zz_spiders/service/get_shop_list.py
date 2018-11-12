# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/10/26
   File Name：     get_shop_list
   Description:
-------------------------------------------------
"""
import datetime
from zz_spiders.utils.mongoDB import Mongodb
import re


def get_shops_list(shop_list_date=None):
    """ 获取店铺列表, 只返回状态为1 的
   """
    if shop_list_date == None:
        shop_list_date = datetime.datetime.now().strftime('%Y-%m-%d')

    client = Mongodb('daily_shops_list', 'zz_web')
    curr_hour = datetime.datetime.now().hour
    shop_list = None
    if curr_hour == 0:
        shop_list_date = datetime.datetime.today() - datetime.timedelta(days=1)
        shop_list_date = shop_list_date.strftime('%Y-%m-%d')
        shop_list = client.find_one({"created_at": re.compile(shop_list_date)})
    else:
        shop_list = client.find_one({"created_at": re.compile(shop_list_date)})
    # shop_list = client.find_one({"updated_at": "2018-10-26 09:21:36"})

    shop_list = shop_list['data']
    shops = []
    for index, shop in enumerate(shop_list):
        if shop['zhitongche_status'] == 1:
            shops.append(shop_list[index])
    return shops
