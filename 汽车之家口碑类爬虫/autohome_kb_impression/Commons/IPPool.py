#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from queue import Queue
from multiprocessing import Queue as mqueue
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from threading import Thread
from time import sleep
from random import random
import requests
import re


class IPPool(Queue):
    '''
    实例化时生成一个自更新的代理IP列队
    '''

    def __init__(self, conn=None, ipurl=None):
        super().__init__()
        self.ipurl = ipurl or 'http://vip22.xiguadaili.com/ip/?tid=556082430314945&num=1000&category=2&protocol=https'
        if conn:
            self.conn = conn
            t_ = Thread(target=self.__refresh_ipurl)
            t_.start()
        t = Thread(target=self.__refresh)
        t.start()
        

    def __refresh_ipurl(self):
        while True:
            if not self.conn.empty():
                url = self.conn.get()
                self.ipurl = url
                print('链接更新成功！')
            sleep(random()*5)

    def __refresh(self):
        while True:
            if self.empty():
                self.__local_refresh()
            else:
                sleep(random()*5)

    def __local_refresh(self):
        header = header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
        try:
            resp = requests.get(self.ipurl, headers=header)
            text = resp.text
            iplist = re.findall(r'((?:(?:\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])\.){3}(?:\d{1,2}|1\d{2}|2[0-4]\d|25[0-5]):\d+)', text)
        except:
            iplist = None
        if iplist:
            for ip in iplist:
                self.put({'https':'https://%s'%ip})
        else:
            print('订单过期或出现网络错误，无法更新代理池！请检查后运行refresh_ipurl(url)替换链接或恢复链接！') 


class IPPoolManager:
    '''代理池管理，用于启动、获取代理池，并在代理池过期后更新代理URL'''

    def __init__(self, ip='localhost', port=16000, authkey='ippool'):
        self.ip = ip
        self.port = port
        self.authkey = authkey

    def run_server(self, ipurl=None):
        p = Process(target=self.inner_q)
        p.start()
        class MyManager(BaseManager): pass
        manager = MyManager((self.ip, self.port), self.authkey.encode('utf-8'))
        conn = self.inner_get_q()
        q = IPPool(conn=conn, ipurl=ipurl)
        print('成功获取到代理列队！')
        manager.register('get_ippool', callable=lambda: q)
        print('创建服务...')
        server = manager.get_server()
        print('成功创建代理池服务！')
        print('代理池运行中...')
        server.serve_forever()

    def get_ippool(self):
        class MyManager(BaseManager): pass
        manager = MyManager((self.ip, self.port), self.authkey.encode('utf-8'))
        manager.register('get_ippool')
        manager.connect()
        return manager.get_ippool()

    def refresh_ipurl(self, url):
        print('链接代理服务...')
        q = self.inner_get_q()
        print('成功获取到列队！')
        q.put(url)
        print('成功添加', url, '到服务！')

    def inner_q(self):
        class innerManager(BaseManager): pass
        q = mqueue(1)
        manager = innerManager((self.ip, self.port+1), self.authkey.encode('utf-8'))
        manager.register('get_q', callable=lambda: q)
        server = manager.get_server()
        server.serve_forever()

    def inner_get_q(self):
        class innerManager(BaseManager): pass
        manager = innerManager((self.ip, self.port+1), self.authkey.encode('utf-8'))
        manager.register('get_q')
        manager.connect()
        return manager.get_q()

