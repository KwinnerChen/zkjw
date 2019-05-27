#! usr/bin/env python3
# -*- coding:utf-8 -*-

from Commons.common import Task
from Commons.task_manager_server import get_queue
from spiders import Spider


def load_task_port():
    with open('task_port_log.log', 'r') as f:
        lines = f.readlines()
        line = lines[1]
        port = line.split(' ')[-1]
        return int(port)


base_url = 'https://k.autohome.com.cn/{carid}/ge0/0-0-2/'
cartype = '帝豪新能源'
carid = '4342'
url = base_url.format(carid=carid)

q = get_queue(('localhost', load_task_port()), b'k')
print('成功获取到人物列队')
spider = Spider()

task = Task(url=url, method='get', callback=spider.content_parse, headers=spider.header, proxies=spider.ippool.get(),temp=cartype)

q.put(task)
print('添加任务成功')





