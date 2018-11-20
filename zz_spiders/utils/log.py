# -*- coding: utf-8 -*-
# 全局存储log方法

import sys
from .mongoDB import Mongodb
from .date import Date

class Log:
    date_cfg = Date()
    mongodb = Mongodb(str(date_cfg.get_today()), 'zz_spiders_log')

    # 一般信息(informational messages)

    def info(self, message, spider, error=None):
        self.save_log(message, spider.name, spider.cookies_id, error, 'INFO')

    # 警告信息(warning messages)

    def warning(self, message, spider, error=None):
        self.save_log(message, spider.name, spider.cookies_id, error, 'WARNING')

    # 一般错误(regular errors)

    def error(self, message, spider, error=None, response=None):
        self.save_log(message, spider.name, spider.cookies_id, error, 'ERROR', response)

    # 严重错误(critical),程序已无法继续运行

    def critical(self, message, spider, error=None):
        self.save_log(message, spider.name, spider.cookies_id, error,  'CRITICAL')

    # log 存储

    def save_log(self, message, spider_name, cookies_id, error, logging, response=None):
        log = {
            'message': str(message),
            'spider': str(spider_name),
            'cookies_id': str(cookies_id),
            'created_at': str(self.date_cfg.get_time()),
            'logging': str(logging),
            'error': str(error),
            'response': str(response)
        }
        response = self.mongodb.save_data(log)
        if response:
            print(response)
