#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


from manager import list_work_thread, task_woker_thread_maker, storage_process
from storage import Oracle
from multiprocessing import Queue, Process
from threading import Thread
# from IPPool_66.IPPool import IPPool
from cache import Cache
from task_manager_server import get_queue, run_task_server
import config
import os


os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


# def proxy_pool(q_proxy, pool):
#     while True:
#         if not q_proxy.full():
#             proxy = pool.get_ip
#             q_proxy.put(proxy)


if __name__ == '__main__':
    # q_proxy = Queue(30)  # 代理列队
    # 关于队列，分布时如果使用队列，则必须使用multiprocessor中的Queue。
    # 运行一个任务列队的服务进程。
    p_task = Process(target=run_task_server, args=((config.TASK_KEY['host'], config.TASK_KEY['port']), config.TASK_KEY['authorkey']))
    p_task.start()

    q_next_url = get_queue(addr=(config.TASK_KEY['host'], config.TASK_KEY['port']), authkey=config.TASK_KEY['authorkey'])
    # q_next_url = Queue(10)
    q_content_task = Queue(config.NEWS_QUEUE_NUM)  # 新闻详情列队，需要分布式，把次列队发布出去。
    q_storage_task = Queue(config.RESAULT_QUEUE_NUM)  # 结果列队，待存
    start_url = config.START_URL
    agent_pool = config.AGENT_POOL
    delay = config.DELAY
    table_name = config.TABLE_NAME
    key_name = config.KEY_NAME

    thread_num = config.THREAD_NUM
    thread_list = []

    # ippool = IPPool()
    cac = Cache()
    db = Oracle(config.DATABASE['user'], config.DATABASE['password'], config.DATABASE['host'])

    # p_proxy = Process(target=proxy_pool, args=(q_proxy, ippool))  # 开启代理池进程
    # p_proxy.start()

    # while True:
    #     if q_proxy.full():
    #         break

    # 新闻列表线程
    # url是列表的起始链接
    list_work_thread(cac, key_name, q_content_task, q_next_url, thread_list, {'agent_pool':agent_pool, 'delay':delay})  # 新闻列表线程
    task_woker_thread_maker(thread_num, thread_list, q_content_task, q_storage_task, {'agent_pool':agent_pool, 'delay':delay})  # 新闻内容线程

    p_storage = Thread(target=storage_process, args=(db, q_storage_task, table_name))
    p_storage.start()


    # 向q_next_url添加启动链接
    # for url in config.START_URL:
    #     q_next_url.put(url)


    # 等待新闻列表线程完成
    for t in thread_list:
        if t.name == 'news_list_thread':
            t.join()
            thread_list.remove(t)


    # 向详情线程添加终止标识
    for i in range(thread_num):
        q_content_task.put(None)


    # 待详情线程结束
    for t in thread_list:
        t.join()


    # 向存储线程添加结束标识
    q_storage_task.put(None)

    # 等待存储完成
    p_storage.join()

    # 终止代理池进程
    # p_proxy.terminate()
    print('爬取结束！')


    
