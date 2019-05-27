#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


import os
import pickle
from datetime import datetime


class Task:
    '''工作在任务流中的任务对象。位置参数和默认参数外的不定量关键字参数将传给下载器，用作下载参数。
    '''
    def __init__(self, url='', method='', callback=None, item=None, temp=None, **kwargs):
        self.url = url
        self.method = method
        self.callback = callback
        self.item = item
        self.temp = temp  # 如果有延续到下个函数的情况下
        self.kwargs = kwargs
    
    def __str__(self):
        string = 'Task(%s)' % ', '.join('%s=%s' % (k,v) for k,v in self.__dict__.items() if v)
        return string
    
    __repr__ = __str__


class BaseSpider:
    '''爬虫基类，每个定义的爬虫都应集成该类，否则无法运行,初始化时接受一个数据结构（可以是None）和一个日志记录器logger。
    '''
    name = ''  # 每个爬虫类的标识，不可重复，在实例化前使用，以确认需要调用的爬虫

    start_urls = []  # 当没有重新定义start_request方法时，自动调用该类变量来生成任务

    def __init__(self, data_struct=None):
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


class REC_NUM:
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


class TimeVerify:
    '''时间验证模块，timeverify用于验证某项目的时间，log_logpkl用于序列化当下验证状态。
       初始化设定限定时间，小于改时间不会通过验证。默认为None，此时时间不做限定。
       ：params：
       :deftime: 限定时间。默认值为None，即不限定时间。此时increment为0时为存量状态，increment为1时为增量状态。
       :increment: 增量模式时为1，此时deftime为None。deftime有值时increment为0。
    '''
    def __init__(self, deftime=None, increment=0):
        if not os.path.exists(os.path.join(os.curdir, 'crawedcar.pkl')) or os.path.getsize(os.path.join(os.curdir, 'crawedcar.pkl')) <=50:
            self.s = {}  # 用于记录已爬取项目于和爬取时间
            self.log_logpkl()
        else:
            self.s = self.__load_logpkl()
        self.deftime = deftime
        self.increment = increment

    def __load_logpkl(self):
        with open('crawedcar.pkl', 'rb') as f:
            s = pickle.load(f)
            return s

    def log_logpkl(self):
        with open('crawedcar.pkl', 'wb') as f:
            pickle.dump(self.s, f)

    def timeverify(self, item, ctime):
        assert self.increment==0 or 1, '增量状态只有0，1两个值，1为增量，0为存量！'
        if not self.deftime and self.increment==1:  # 此时为增量状态，与保存中的状态进行验证
            if item not in self.s:
                if ctime > '2017-01-01':
                    return True
                else:
                    self.s[item] = datetime.now().strftime('%Y-%m-%d')
                    return False
            if ctime > self.s[item]:
                return True
            else:
                self.s[item] = datetime.now().strftime('%Y-%m-%d')
                return False
        elif not self.deftime and self.increment==0:  # 此时为存量状态，不做验证，只更新状态
            self.s[item] = datetime.now().strftime('%Y-%m-%d')
            return True
        elif self.deftime and self.increment==0:  # 此时为限定存量状态，限定时间，并更新状态
            if ctime >= self.deftime:
                return True
            else:
                self.s[item] = datetime.now().strftime('%Y-%m-%d')
                return False

            
class Erro:
    '''一个错误任务对象，只是为了区别Task对象'''
    def __init__(self, url, mess, callback, **kwargs):
        self.url = url
        self.mess = mess
        self.kwargs = kwargs
        self.callback = callback
        if kwargs:
            for k,v in kwargs.items():
                self.__setattr__(k,v)

    def __str__(self):
        string = 'Erro(%s)' % ', '.join('%s=%s' % (k,v) for k,v in self.__dict__.items() if v)
        return string
    
    __repr__ = __str__
