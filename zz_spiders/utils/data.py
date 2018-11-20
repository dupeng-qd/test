# -*- coding: utf-8 -*-
"""
    本文件用于编写 处理数据通用方法
"""
import json
import re
import pymysql
from zz_spiders.env import env

class Data:

    # jsonp 解析

    def jsonp(self, response):
        try:
            return json.loads(re.findall(r'^\w+\((.*)\)$', response)[0])
        except Exception as e:
            return json.loads(re.findall(r'^\w+\((.*)\);$', response)[0])

    # 从页面取到的字段 转化 成数据库字段
    def mysql_column(self, table, key, value):
        db = pymysql.connect(host=env['mysql_shop_data']['db_host'], port=int(env['mysql_shop_data']['db_port']),
                             user=env['mysql_shop_data']['username'], passwd=env['mysql_shop_data']['password'],
                             db=env['mysql_shop_data']['db_name'], charset=env['mysql_shop_data']['charset'])
        cursor = db.cursor()
        # 因为字段是直接从response转化得到，有可能有多余字段，进行去除多余字段
        # 查询数据库的所有字段
        sql_column = "select COLUMN_NAME from information_schema.COLUMNS where table_name = '{}';".format(table)
        cursor.execute(sql_column)
        column_table = cursor.fetchall()

        # 循环去除多余字段
        for i, v in enumerate(key):
            if (v,) not in column_table:
                key.pop(i)
                value.pop(i)

        # 将字段列表转成字符串
        k = ', '.join(i for i in key)

        # 格式化（{}format传列表）
        v = []
        va = ''
        for i in range(len(key)):
            v.append('{0[' + str(i) + ']}')
            va = "', '".join(v)
        # 插入 sql 语句，用format
        sql = "insert into " + table + " (" + k + ") values('" + va + "')"
        # 格式化传值
        sql_exe = sql.format(value)

        # 往数据库插入数据
        cursor.execute(sql_exe)
        db.commit()
        cursor.fetchall()
