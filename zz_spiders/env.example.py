# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/10/24
   File Name：     env
   Description:    配置文件
-------------------------------------------------
"""

# 每个爬虫爬取店铺数
avg_spiders = 100.0

# url
api_zhitongche_url = 'http://jupinzhuanche.hz.taeapp.com/zz-jushita-zhitongche-pro'
api_zuanzhan_url   = 'http://jupinzhizuan.hz.taeapp.com/zz-jushita-zuanzhan-pro'

env = {
  # mysql 配置数据
  'mysql_config': {
    'db_host': 'slave1.mysql.boss.jupin.net.cn',  # 设置默认数据连接地址
    'db_port': '3306',  # 设置默认端口号
    'db_name': 'jupin_erp_business',  # 设置默认数据库
    'username': 'jupin_api',  # 设置默认用户名
    'password': '41Yo3LtEcVS38y70',  # 设置默认密码
    'charset': 'utf8',  # 设置默认字符集
  },

  # mongodb 配置数据
  'mongodb_config': {
    'host': '192.168.1.196',
    'port': 27017,
    'user': None,
    'password': None,
    'auth_db': 'admin',
    'data_db': {
      'zz_web': 'zz_web',
    }
  },

  # redis 配置数据
  'redis_config': {
    'host': '192.168.1.63',
    'port': '6379',
    'password': None,
    },

  #scrapyd 配置地址
  'scrapyd_url': 'http://localhost:6800'
}