#! usr/bin/env python3
# -*- coding: utf-8 -*-


import config
from multiprocessing import Process, Queue
from threading import Thread
from task_manager_server import run_task_server, get_queue
from IPPool.IPPool import IPPool
from storage import DB
from spider import log_url, proxiy_pool, worker, thread_maker, thread_worker, storage_process


if __name__ == '__main__':
    p_task_server = Process(target=run_task_server, args=(config.ADDR, config.AUTHKEY))
    p_task_server.start()  # 启动一个任务服务进程

    q_task = get_queue()  # 从管理进程中获取任务队列
    q_proxiy = Queue(20)  # 代理IP队列
    q_result = Queue(10)  # 结果待存队列
    
    thread_list = []  # 线程列表
    ippool = IPPool()
    task_thread_num = config.THREAD_NUM
    area = config.AREA
    logger = log_url(config.LOGNAME)
    task_keyword_list = config.TASK_LIST  # 任务列表

    db = DB(host=config.DATABASE['host'], port=config.DATABASE['port'], user=config.DATABASE['user'], password=config.DATABASE['password'], db=config.DATABASE['db'])
 
    p_proxy = Process(target=proxiy_pool, args=(ippool, q_proxiy))  # 开启一个代理IP进程
    p_proxy.start()

    while True:
        if q_proxiy.full():
            break

    thread_maker(area, config.SITES, q_task, q_proxiy, q_result, logger, task_thread_num, thread_worker, thread_list)  # 本地进程开启task_thread_num个任务线程，并监听任务

    p_storage = Thread(target=storage_process, args=(db, config.DATABASE['table_name'], q_result))  # 开启一个数据库存储线程，并监听任务
    p_storage.start()
      
    for i in range(len(task_keyword_list)):
        q_task.put(task_keyword_list.pop())  # 向任务列队中添加任务

    for n in range(task_thread_num):
        q_task.put(None)  # 向任务队列中添加终止标示，分布时可以注释掉，由任务服务添加

    for t in thread_list:
        t.join()  # 等待所有线程结束

    # p_task_server.terminate()  # 终结任务服务器，分布时注释掉

    p_proxy.terminate()  # 主动终结代理进程

    q_result.put(None)  # 向存储任务列队添加终止标示。
    p_storage.join()  # 等待存储任务完成。
    
    print('爬取完成！')
    input()