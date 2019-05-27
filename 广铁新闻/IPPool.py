#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from storage import Oracle
from queue import Queue
from threading import Thread
from time import sleep
from random import random


class IPPool(Queue):
    '''
    实例化时生成一个自更新的代理IP列队
    '''
    def __init__(self, user, password, host, table_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.password = password
        self.host = host
        self.table_name = table_name
        # self.delay_time = delay_time
        t = Thread(target=self.__refresh)
        t.start()

    def __refresh(self):
        while True:
            if self.empty():
                self.__put_proxy_queue()
            else:
                sleep(random()*2)
    
    def __get_proxy_database(self):
        ora = Oracle(self.user, self.password, self.host)
        data = ora.getall(self.table_name)
        ora.close()
        return data

    def __put_proxy_queue(self):
        data = self.__get_proxy_database()
        for ip, http in data:
            self.put({http: http + '://' + ip})
    
