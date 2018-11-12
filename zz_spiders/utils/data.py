# -*- coding: utf-8 -*-
"""
    本文件用于编写 处理数据通用方法
"""
import json
import re

class Data:

    # jsonp 解析

    def jsonp(self, response):
        try:
            return json.loads(re.findall(r'^\w+\((.*)\)$', response)[0])
        except Exception as e:
            return json.loads(re.findall(r'^\w+\((.*)\);$', response)[0])
