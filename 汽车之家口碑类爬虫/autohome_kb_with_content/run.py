#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


import config
import time
import typing
from datetime import datetime
from re import match
from Commons.manager import storage_threading, download_threading, result_threading
from Commons.downloader import Downloader
from multiprocessing import Queue, Process
from threading import Thread
from Log.log import get_a_logger
from Commons.common import Task
from Commons.task_manager_server import run_task_server
from Cookie.Cookies import get_cookie_from_url


if config.WETHER_DB and config.DBNAME.lower() == 'oracle':
    import os
    os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


def log_task_port(spider_name, port):
    with open('task_port_log.log', 'w') as f:
        f.write('\n%s  %s: %s\n' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), spider_name, port))

def task_num_check(q_task, q_reault, q_storage, q_proxy, logger, thread_list):
    while True:
        if not thread_list:
            break
        task_num = q_task.qsize() if q_task else None
        reault_num = q_reault.qsize() if q_reault else None
        storage_num = q_storage.qsize() if q_storage else None
        proxy_num = q_proxy.qsize() if q_proxy else None
        logger.info('\n任务列队长度：%s  中间列队长度：%s  存储列队长度：%s  代理列队长度：%s\n' % (task_num, reault_num, storage_num, proxy_num))
        time.sleep(5)

def check_thread(q_task, q_reault, q_storage, q_proxy, logger, thread_list):
    t = Thread(target=task_num_check, args=(q_task, q_reault, q_storage, q_proxy, logger, thread_list))
    t.start()

# def run_server(ip, port, authkey, url):
#     from Commons.IPPool import IPPoolManager
#     manager = IPPoolManager(ip, port, authkey)
#     manager.run_server(url)
    

if __name__ == '__main__':
    import sys
    argvs = sys.argv
    arg = argvs[1]
    table_name = config.TABLE_NAME  # 当传参没有指定数据表名时，使用配置文件中的默认表名
    if len(argvs) >= 3:
        assert len(table_name) <= 30, '表名过长！'
        assert match(r'\w', table_name), '不能以非法字符开头！'
        table_name = argvs[2]
    q_task = Queue(config.Q_TASK_SIZE)
    # 将任务列队发布出去，以便在运行时可以添加任务或停止任务
    # 任务运行期间可以使用task_manager_server中的get_queue函数获取该列队
    p = Process(target=run_task_server, args=(q_task, (config.TASK_KEY.get('addr'), config.TASK_KEY.get('port')), config.TASK_KEY.get('authkey')))
    p.start() 
    # 代理ip池
    # if config.WETHER_IPPOLL:
    #     from Commons.IPPool import IPPoolManager
    #     manager = IPPoolManager(ip=config.PROXY.get('ip'), port=config.PROXY.get('port'), authkey=config.PROXY.get('authkey'))
    #     p_proxy = Process(target=run_server, args=(config.PROXY.get('ip'),config.PROXY.get('port'),config.PROXY.get('authkey'),config.PROXY_URL))
    #     p_proxy.start()
    #     q_proxy = manager.get_ippool()
        # q_proxy = None
    if not config.WETHER_IPPOLL:
        q_proxy = None
    q_reault = Queue(config.Q_REAULT_SIZE)
    logger = get_a_logger(config.LOGFILE_NAME)
    d_thread_num = config.D_THREAD_NUM
    r_thread_num = config.R_THREAD_NUM  
    data_struct = config.DATA_STRUCT
    delay = config.DELAY
    timeout = config.TIMEOUT
    thread_list = []  # 一个线程实例的容器
    log_task_port(arg, config.TASK_KEY.get('port'))  # 记录当前爬虫任务列队的端口


    # 实例一个下载器，将获取到的cookie加入会话，在同域链接访问中共享cookie
    class MyDownloader(Downloader): pass
    downloader = MyDownloader()
    if config.COOKIES:
        if isinstance(config.COOKIE, dict):
            downloader.set_cookie(config.COOKIE)
        elif isinstance(config.COOKIE, str):
            cookies = get_cookie_from_url(config.COOKIE)
            downloader.set_cookie(cookies)


    # 启动各线程，监听任务
    if config.WETHER_DB:
        exec('from Commons.storage import %s as DB' % config.DBNAME.title())
        s_thread_num = config.S_THREAD_NUM
        q_storage = Queue(config.Q_STORAGE_SIZE)
        db = DB(**config.LINK)
        storage_threading(db, table_name, data_struct, q_storage, logger, s_thread_num, thread_list)
    if not config.WETHER_DB:
        q_storage = None
    download_threading(downloader, q_task, q_reault, d_thread_num, thread_list, logger, delay, timeout=timeout)
    result_threading(q_reault, q_task, q_storage, r_thread_num, thread_list, logger)
    check_thread(q_task, q_reault, q_storage, q_proxy, logger, thread_list)


    # 爬虫模块必须在配置文件中注册，完整的引用路径
    # 由初始链接初始化爬虫实例
    # 由start_requests方法生成初始Task任务对象，放入任务列队
    for sp in config.SPIDERS:
        exec('from %s import %s' % (sp.split('.')[0], sp.split('.')[1]))

    for sp, num in zip(config.SPIDERS, range(len(config.SPIDERS))):
        if eval(sp.split('.')[-1]+'.name') == arg:
            exec('%s_%d = %s(%s)' % (sp.split('.')[-1].lower(), num, sp.split('.')[1], data_struct))
            exec('gener = %s_%d.start_request()' % (sp.split('.')[1].lower(), num))
            if isinstance(gener, (typing.Iterable, typing.Iterator, typing.Generator)):
                for task in gener:
                    q_task.put(task)
                    logger.info('添加到任务列队：%s' % task)
            else:
                q_task.put(gener)
                logger.info('添加到任务列队：%s' % gener)


    # 等待下载线程结束
    for t in thread_list:
        if 'download' in t.name:
            t.join()
            logger.warning('下载线程'+t.name+'结束！')
            thread_list.remove(t)


    # 下载线程结束后，向中间的结果列队添加终止标识None
    # 有几个线程添加几个
    for i in range(r_thread_num):
        q_reault.put(None)
    # 等待中间处理线程完成
    for t in thread_list:
        if 'reault' in t.name:
            thread_list.remove(t)
            logger.warning('处理线程'+t.name+'结束！')
            t.join()


    # 待中间列队处理完毕，向存储列队添加终止标识None
    # 有几个线程添加几个
    if config.WETHER_DB:
        for i in range(s_thread_num):
            q_storage.put(None)
        # 等待存储线程完成
        for t in thread_list:
            t.join()
            logger.warning('存储线程'+t.name+'结束！')

    thread_list.clear()
    

    # 关闭数据库会话池
    if config.WETHER_DB:
        db.close()
        logger.warning('关闭数据库！')
    logger.warning('任务结束！')
    p.terminate()  # 结束任务进程
    p_proxy.terminate()
    # input('任意键推出...')
    # exit()   
