# -*- coding: utf-8 -*-

# 每日执行的计划任务调用此文件
# 每日计划任务流程:
# 1、获取店铺列表，判断是否存在当日的店铺列表（直通车、钻展）
#     假如存在店铺列表执行获取数据爬虫，假如不存在店铺列表则 执行店铺列表的采集
# 2、检测当日未执行爬虫，执行这些爬虫 （根据爬虫执行log，获取爬虫状态）
# 3、获取直通车和钻展空闲账号，分配给未执行爬虫，进行数据采集（根据爬虫执行log，获取账号状态）

import sys
import os
from zz_spiders.env import avg_spiders
from zz_spiders.env import env
from multiprocessing import Process
from zz_spiders.service.get_shop_list import get_shops_list
from zz_spiders.utils.date import Date
import math


def spider_subprocess(spider_index_begin, spider_index_end):
    # shell = env['scrapyd_url'] + '/schedule.json -d project=zz_spiders -d spider=zhitongche.real_time_data -d begin={} -d end={}'.format(spider_index_begin, spider_index_end)
    # os.system('curl ' + shell)
    # shell = env['scrapyd_url'] + '/schedule.json -d project=zz_spiders -d spider=zhitongche.campaign.real_time_data -d begin={} -d end={}'.format(spider_index_begin, spider_index_end)
    # os.system('curl ' + shell)
    # if Date().get_now_hour() == 5:
    #     shell = env['scrapyd_url'] + '/schedule.json -d project=zz_spiders -d spider=zhitongche.shop.shop_history_data -d begin={} -d end={}'.format(spider_index_begin, spider_index_end)
    #     os.system('curl ' + shell)
    os.system('scrapy crawl zhitongche.campaign.real_time_data -a begin={} -a end={}'.format(spider_index_begin, spider_index_end))

def run_spider(shop_list=None):
    spider_num = math.ceil(len(shop_list)/avg_spiders)
    for i in range(int(spider_num)):
        Process(target=spider_subprocess, args=(int(i*avg_spiders), int(i*avg_spiders+avg_spiders))).start()


def main():
    shop_list = get_shops_list()
    if shop_list:
        run_spider(shop_list)


if __name__ == "__main__":
    main()