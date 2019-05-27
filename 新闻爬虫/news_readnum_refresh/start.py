#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v 3.6.4


import os
import socket
from Commons.task_manager_server import get_queue
from config import TASK_KEY
from spider import Spider


def load_task_port():
    with open('task_port_log.log', 'r') as f:
        lines = f.readlines()
        line = lines[1]
        port = line.split(' ')[-1]
        return int(port)

def check_port(port):
    s = socket.socket()
    r = s.connect_ex(('localhost', port))
    if r == 0:
        return True
    else:
        return False
    s.close()

if __name__ == '__main__':
    if os.path.exists('task_port_log.log'):
        port = load_task_port()
        assert check_port(port), '爬虫未启动！'
        q = get_queue((TASK_KEY['addr'], port), TASK_KEY['authkey'])
        spider = Spider()
        for task in spider.start_request():
            q.put(task)
    else:
        os.system('python run.py news_refresh')