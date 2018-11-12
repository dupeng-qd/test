# -*- coding: utf-8 -*-

import scrapy

import requests
import time
import random
import logging
import datetime
from urllib import parse


class SpiderRequest:
    now = None
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/53",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    random_ua = None

    def __init__(self):
        self.random_ua = random.choice(self.user_agent_list)
        self.now = datetime.datetime.now()
        # 睡眠

    def __get_time_out(self):
        return random.randint(1, 3)
    def __get_long_time_out(self):
        return random.randint(0, 3)

    def sleep(self, start_time=None):
        time_out = self.__get_time_out()
        logging.info("爬虫随机昏睡：" + str(time_out) + "秒")
        time.sleep(time_out)

    def longSleep(self, start_time=None):
        time_out = self.__get_long_time_out()
        logging.info("爬虫随机昏睡：" + str(time_out) + "秒")
        time.sleep(time_out)

    def get(self, url='', params={}, cookies={}, headers={}, start_time=None, is_json=1):
        self.sleep()
        # 随机的User-Agent
        headers['User-Agent'] = self.random_ua
        if is_json==1:
            response = requests.get(url, params=params, cookies=cookies, headers=headers).json()
        else:
            response = requests.get(url, params=params, cookies=cookies, headers=headers)
        return response

    def post(self, url='', data={}, cookies={}, headers={}, start_time=None,is_json=1):
        self.sleep()
        # 随机的User-Agent
        headers['User-Agent'] = self.random_ua
        if is_json == 1:
            response = requests.post(url, data=data, cookies=cookies, headers=headers).json()
        else:
            response = requests.post(url, data=data, cookies=cookies, headers=headers)
        return response

    def scrapy_get(self, url='', cookies={}, headers={}, callback=None, start_time=None):
        return scrapy.Request(
            url=url,
            method='GET',
            cookies=cookies,
            headers=headers,
            callback=callback,
        )

    def scrapy_post(self, url='', body={}, cookies={}, headers={}, callback=None, start_time=None):
        return scrapy.Request(
            url=url,
            method='POST',
            body=parse.urlencode(body),
            cookies=cookies,
            headers=headers,
            callback=callback
        )

    def scrapy_form_post(self, url='', cookies={}, formdata={}, callback=None):
        return scrapy.FormRequest(
            url=url,
            method='POST',
            formdata=formdata,
            # meta={'key':item},
            cookies=cookies,
            callback=callback,
            dont_filter=True
        )

    def scrapy_form_get(self, url='', cookies={}, formdata={}, callback=None):
        return scrapy.FormRequest(
            url=url,
            method='GET',
            formdata=formdata,
            # meta={'key':item},
            cookies=cookies,
            callback=callback,
            dont_filter=True
        )