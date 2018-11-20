# -*- coding: utf-8 -*-

"""    
    本文件用于编写 关于时间的通用方法
"""

import datetime
import time

class Date:

    # 获取当前时分秒日期
    def get_time(self):
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return time

    # 获取当前毫秒数

    def get_now_time(self):
        t = time.time()
        nowTime = lambda: int(round(t * 1000))
        nowTime = str(nowTime())
        return nowTime


    # 获取当前的小时

    def get_now_hour(self):
        hour = datetime.datetime.now().hour
        return hour

    # 获取上个小时的时间
    def get_last_hour(self):
        hour = datetime.datetime.now().hour
        if(hour - 1 < 0 ):
            hour = 23
        else:
            hour = hour - 1
        return hour

    # 获取昨天

    def get_yesterday(self):
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        return yesterday

    # 获取今天日期

    def get_today(self):
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        return today

    # 获取从某一天开始几天前日期（不包括startDay）

    def get_other_day(self, startDay, day):
        oneday = datetime.timedelta(days=int(day))
        yesterday = startDay - oneday
        return yesterday
