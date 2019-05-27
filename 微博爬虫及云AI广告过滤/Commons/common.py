#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


class Task():
    def __init__(self, url='', method='', callback=None, item=None, temp=None):
        self.url = url
        self.method = method
        self.callback = callback
        self.item = item
        self.temp = temp  # 如果有延续到下个函数的情况下
    
    def __str__(self):
        string = 'Task(%s)' % ', '.join('%s=%s' % (k,v) for k,v in self.__dict__.items() if v)
        return string
    
    __repr__ = __str__


class BaseSpider():

    name = ''  # 每个爬虫类的标识，不可重复，在实例化前使用

    start_urls = []

    def __init__(self, data_struct):
        self.data_struct = data_struct

        # 该方法将初始链接生成任务对象
    def start_request(self):
        if isinstance(self.start_urls, (list, tuple)):
            for u in self.start_urls:
                yield Task(url=u, method='get', callback=self.response_parse)
        elif isinstance(self.start_urls, str):
            yield Task(url=self.start_urls, method='get', callback=self.response_parse)

    # 必须定义的方法，用于处理start_request返回的相应对象
    def response_parse(self, response):
        pass


class REC_NUM():
    '''
    一个计数器
    '''

    def __init__(self):
        self.count = 1

    def addone(self):
        self.count += 1

    def reset(self):
        self.count = 1

    def __str__(self):
        return str(self.count)

    __repr__ = __str__

    



            