#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen


from multiprocessing.managers import BaseManager
from multiprocessing import Queue


'''
    实现一个任务管理器，其中只有一个任务列队。
    开启任务管理器：
    >>> from task_manager_server import run_task_server
    >>> run_task_server(addr::tuple, authkey::binstr)  # 服务会持续运行，直到报错或手动关闭
    获取任务列队：
    >>> q = get_queue(addr::tuple, authkey::binstr)
    >>> task = q.get()
    >>> q.put(atask)
'''


class TaskManager():
    def __init__(self, addr, authkey):
        class MyManager(BaseManager): pass
        self.manager = MyManager(addr, authkey)


    def start_server(self, q):
        self.manager.register('get_task_queue', callable=lambda: q)
        server = self.manager.get_server()
        server.serve_forever()


    def connect(self):
        self.manager.register('get_task_queue')
        self.manager.connect()


    def get_queue(self):
        return self.manager.get_task_queue()


def run_task_server(q, addr, authkey):
    # q为要发布出去的任务列队
    manager = TaskManager(addr, authkey)
    manager.start_server(q)


def get_queue(addr, authkey):
    manager = TaskManager(addr, authkey)
    manager.connect()
    return manager.get_queue()
