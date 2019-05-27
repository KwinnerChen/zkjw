#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from threading import Thread
from Commons.downloader import Downloader
from Commons.common import Task, Erro
from datetime import datetime
from typing import Iterable, Generator, Iterator
import time
import random
import os


def storage_threading(db, table_name, data_struct, q_storage, logger, thread_num, thread_list):
    for i in range(thread_num):
        t = Thread(name='storage_threading_%s' % i, target=storage_worker, args=(db, table_name, data_struct, q_storage, logger))
        thread_list.append(t)
        t.start()
        logger.warning(t.name + ' 启动！')


# 存储主函数，日志记录错误
def storage_worker(db, table_name, data_struct, q_storage, logger):
    while True:
        if not q_storage.empty():
            r = q_storage.get()
            if r is None:
                break
            try:
                logger.info('\n存储数据：%s\n' % r)
                storage(db, table_name, data_struct, r)
                logger.info('\n%s 条数据存入数据库\n' % len(r))
                del r
            except Exception as e:
                erro = str(e)
                status = storage_meet_error(db, erro, table_name, data_struct, r, logger)
                if status:
                    logger.warning('\n'+str(r)+'存储出错！%s\n' % status)
                    del r
                del erro
                del status
        else:
            time.sleep(random.random())


def storage_meet_error(db, erro, table_name, data_struct, r, logger):
    n = 0
    while True:
        if '会话' in erro or '连接' in erro:
            try:
                db.reconnect()
                storage(db, table_name, data_struct, r)
                logger.info('\n%s 条数据存入数据库\n' % len(r))
            except Exception:
                time.sleep(5)
                continue
            else:
                return
        else:
            try:
                storage(db, table_name, data_struct, r)
                logger.info('\n%s 条数据存入数据库\n' % len(r))
            except Exception as e:
                if n > 2:
                    return str(e)
                n += 1
                time.sleep(5)
                continue
            else:
                return            
        

def storage(db, table_name, data_struct, r):
    db.try_to_create_table(table_name, data_struct)
    if len(r) > 1:
        db.savemany(table_name, data_struct, r)
    elif len(r) == 1:
        db.save(table_name, data_struct, r[0])


# 从任务列队中取出Task对象，用于下载对象任务
# response对象加入Task对象，并加入一个中间队列q_result，待处理
def download_worker(downloader, thread_name, q_task, q_result, logger, delay, kwargs):
    while True:
        if not q_task.empty():
            task = q_task.get()
            if task is None:
                break
            try:
                logger.info('\n下载线程%s正在下载：%s\n' % (thread_name, task))
                resp = download(downloader, task, delay, **kwargs)
                task.response = resp
                q_result.put(task)
                logger.info('\n加入到中间列队：%s\n' % task)
            except Exception as e:
                logger.warning('\n%s 下载出错！%s\n' % (task.url, e))
                erro = Erro(url=task.url, method=task.method, mess=str(e), callback=task.callback, temp=task.temp, item=task.item)
                task.response = erro
                q_result.put(task)
                logger.warning('\n%s 返回中间列队等待处理！%s\n' % (task.url, e))
                del erro
        else:
            time.sleep(random.random())


def download(downloader, task, delay, **kwargs):
    url = getattr(task, 'url')
    method = getattr(task, 'method')
    kwarg = getattr(task, 'kwargs')
    if url:
        if kwarg:
            kwargs.update(kwarg)
        if method == 'get':
            time.sleep(delay)
            resp = downloader.get(url, **kwargs)
            resp.raise_for_status  
        if method == 'post':
            time.sleep(delay)
            resp = downloader.post(url, **kwargs)
            resp.raise_for_status
    else:
        resp = None
    return resp


def download_threading(downloader, q_task, q_result, thread_num, thread_list, logger, delay, **kwargs):
    for i in range(thread_num):
        thread_name = 'download_threading_%s' % i
        t = Thread(name=thread_name, target=download_worker, args=(downloader, thread_name, q_task, q_result, logger, delay, kwargs))
        thread_list.append(t)
        t.start()
        logger.warning(t.name + ' 启动！')


# 对从q_result列队中的Task对象进行处理，调用Task对象中的回掉函数
# 分支判断Task处理结果放入q_storage列队或者放回q_task列队继续下载
# 写的略low啊！！！！！！
def result_worker(result, q_task, q_storage, logger):
    response = getattr(result, 'response')
    if response:
        callback = result.callback
        logger.info('\n正在解析：%s\n' % result)
        if result.temp:
            try:
                data = callback(response, result.temp)
            except Exception as ex:
                logger.warning('\n没有解析出数据：%s Erro:%s\n' % (result, ex))
                data = None
        else:
            try:
                data = callback(response)  # 回调函数返回值
            except Exception as e:
                logger.warning('\n没有解析出数据：%s Erro:%s\n' % (result, e))
                data = None
        process_data(data, q_task, q_storage, logger)
    else:
        if result.url:
            logger.warning(result.url + '响应对象为空!返回任务列队！')
            q_task.put(result)


def process_data(data, q_task, q_storage, logger):
    if data:
        wether_task(data, q_task, q_storage, logger)
        

def wether_task(task, q_task, q_storage, logger):
    if isinstance(task, Task):
        if task.item:
            q_storage.put(task.item)
            logger.info('\n有item加入到存储列队：%s\n' % task.item)
            if task.url:
                task.item = None  # 重新初始化item
                q_task.put(task)
                logger.info('\n帖子翻页加入任务列队：%s\n' % task)
            else:
                del task
        else:
            q_task.put(task)
            logger.info('\n有任务加入到任务列队：%s\n' % task)
    elif isinstance(task, (Generator, list, tuple)):
        for i in task:
            wether_task(i, q_task, q_storage, logger)


def result_alloter(q_result, q_task, q_storage, logger):
    while True:
        if not q_result.empty():
            result = q_result.get()
            if result is None:
                break
            result_worker(result, q_task, q_storage, logger)
        else:
            time.sleep(random.random())


def result_threading(q_result, q_task, q_storage, thread_num, thread_list, logger):
    for i in range(thread_num):
        t = Thread(name='reault_threading_%s' % i, target=result_alloter, args=(q_result, q_task, q_storage, logger))
        thread_list.append(t)
        t.start()
        logger.warning(t.name + ' 启动！')


