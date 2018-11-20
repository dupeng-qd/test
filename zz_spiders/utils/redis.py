# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   date：          2018/10/24
   File Name：     save_redis
   Description:
-------------------------------------------------
"""
from zz_spiders.env import env
import redis


class RedisDatabase:
    redis_host = env['redis_config']['host']
    redis_port = env['redis_config']['port']
    pool = redis.ConnectionPool(host=redis_host, port=redis_port, decode_responses=True)

    redis_client = redis.Redis(connection_pool=pool)

    def save_data(self, key, item):
        self.redis_client.set(key, item)
        # print(key, item)
        # print()

    def get_data(self, key):
        return self.redis_client.get(key)

    def exists(self, key):
        return self.redis_client.exists(key)

