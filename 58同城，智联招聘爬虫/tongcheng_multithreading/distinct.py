#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import redis


class DisFilter():
    '''使用本地的redis数据库做缓存，用其set类型做去重'''

    def __init__(self, user=None, password=None, host='localhost', port=6379):
        self.pool = redis.ConnectionPool()
        self.cli = redis.Redis(host=host, port=port, connection_pool=self.pool)

    def check(self, key, value):
        # 使用redis中国的set类型用于去重
        return self.cli.sadd(key, value)
