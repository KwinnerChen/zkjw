#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.7


import redis


class Cache():
    '''
        使用Redis数据库作为缓存，实现去重，数据固化，之后可用作增量缓存。使用连接池管理链接的建立与断开。
        :params:
        :key_name: set类型的名称。
        :kwargs: 不定量关键字参数，包含host，port，password，和db。
    '''
    def __init__(self, **kwargs):
        pool = redis.ConnectionPool(**kwargs)
        self.redis = redis.Redis(connection_pool=pool, )

    def varify(self, key_name, *values):
        '''
            将值存储于set类型中，返回存入值得个数，所以当存入重复值时，返回的是0。
            :params:
            :values: 不定量位置参数，可以同时传入多个值。
        '''
        r = self.redis.sadd(key_name, *values)
        return r