#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


from downloader import page_downloader
from page_parse import news_info_parse, news_list_parse
from log import log
from threading import Thread
import re
import time
import random


logger = log('log.txt')


# 下载新闻列表并分析，返回([(title, url, read_num)[,...]], next_url) next_url是下一页新闻列表链接
def news_list(url, cac, key_name, q_next_url, q_content_task, **kwargs):
    print('开始下载', url, '\n')
    resp = page_downloader(url, **kwargs)
    # print(resp)    
    if resp:
        # logger.info(url + '下载完成！')
        list_tuple, next_url = news_list_parse(resp)
        print('开始解析', url)
        if not next_url:
            # next_url = None
            logger.warning(url+'后无跟踪链接！')
        if next_url:
            q_next_url.put(next_url)
        if list_tuple:
            for i in list_tuple:
                if i and cac.varify(key_name, i[1]):
                    q_content_task.put(i)
                    print(i, '加入详情列队...\n')
                else:
                    print(i, '以获取...\n')
        if not list_tuple:
            logger.warning(url+'没有新闻列表！')
        # logger.info(url + '解析完成！')
        # print(list(list_tuple))
    else:
        # q_next_url.put(None)
        logger.warning(url+' 下载出错！')
        
    


# 下载并处理新闻详情页
def news_info(url, info_dict, **kwargs):
    print('开始下载', url, '\n')
    resp = page_downloader(url, **kwargs)
    if not resp:
        logger.warning(url+' 下载出错！')
    print('开始解析', url, '\n')
    dic = news_info_parse(resp, info_dict)
    if not dic:
        logger.warning(url+' 没有解析出任何数据！')
    # print(dic)
    return dic


# 处理新闻列表页，解析出的数据放入任务列队，翻页
def list_work(cac, key_name, q_content_task, q_next_url, kwargs):
    while True:
        if not q_next_url.empty():
            next_url = q_next_url.get()
            if next_url is None:
                break
            news_list(next_url, cac, key_name, q_next_url, q_content_task, **kwargs)
        else:
            time.sleep(random.random())


# 新闻列表线程
def list_work_thread(cac, key_name, q_content_task, q_next_url, thread_list, kwargs):  # kwargs是一个参数字典
    t = Thread(target=list_work, args=(cac, key_name, q_content_task, q_next_url, kwargs), name='news_list_thread')
    t.start()
    logger.info('-'*20 + '新闻列表线程开始' + '-'*20)
    thread_list.append(t)


# 将解析到的详情放入结果列队待存
def content_work(url, info_dict, q_storage_task, **kwargs):
    print('开始解析', url, '\n')
    dic = news_info(url, info_dict, **kwargs)
    if dic and dic['TITLE']:
        q_storage_task.put(dic)
        print(url, '加入存储列队...\n')
    else:
        logger.warning(url+' 没有解析出数据！')
        

# 任务线程函数，获取任务，结果放入存储列队
def task_worker(q_content_task, q_storage_task, kwargs):
    # list_work(url, q_content_task, **kwargs)
    while True:
        if not q_content_task.empty():
            task = q_content_task.get()
            print('获取到详情任务：', task, '\n')
            if task is None:
                break
            info_dict = {}
            url = task[1]
            try:
                comments_num = get_comments(task[-1])
            except Exception as e:
                print('获取comments_num出错', e)
                comments_num = ''
            # print('comments_num', comments_num)
            info_dict['TITLE'] = task[0]
            info_dict['URL'] = url
            info_dict['READ_NUM'] = task[2] if '万' not in str(task[2]) else str(int(float(task[2].replace('万', ''))*10000))
            info_dict['COMMENTS_NUM'] = comments_num
            content_work(url, info_dict, q_storage_task, **kwargs)
        else:
            print('等待任务...', end='\r')
            time.sleep(random.random())


def get_comments(comments_id):
    url = 'https://reply.autohome.com.cn/api/getData_ReplyCounts.ashx?appid=1&dateType=jsonp&objids={0}&callback=jQuery17206589017939683379_{1}'.format(comments_id, int(time.time()*1000))
    resp = page_downloader(url)
    html = resp.text
    # print('comments_text', html)
    comments_num = re.search(r'"replycountall":(\d+),', html).group(1)
    return comments_num


# 线程创建函数
def task_woker_thread_maker(thread_num, thread_list, q_content_task, q_storage_task, kwargs):
    for i in range(thread_num):
        t = Thread(target=task_worker, args=(q_content_task, q_storage_task, kwargs), name='task_thread '+str(i))
        t.start()
        logger.info('任务线程 %s 启动！' % i)
        thread_list.append(t)        


# def storage_process(db, q_storage_task, table_name, cont_num=30):  # db链接到已定数据库
#     while True:
#         r_list = []
#         try:
#             for i in range(cont_num):
#                 r = q_storage_task.get()
#                 if r is None:
#                     raise StopIteration
#                 r_list.append(r)
#         except StopIteration:
#             try: 
#                 db.savemany(r_list, table_name)
#                 print(''.join(['向',table_name, '存入', str(len(r_list)), '条数据！\n']))
#             except Exception as e:
#                 if str(e)[:4] == '2055':
#                     logger.warning('数据库链接关闭，重新链接...')
#                     db.reconnect()
#                     db.savemany(r_list, table_name)
#                     print(''.join(['向',table_name, '存入', str(len(r_list)), '条数据！\n']))
#                 else:
#                     logger.info(str(r_list) + '存储出错：%s' % e)
#             break
#         else:
#             try: 
#                 db.savemany(r_list, table_name)
#                 print(''.join(['向',table_name, '存入', str(len(r_list)), '条数据！\n']))
#             except Exception as e:
#                 if str(e)[:4] == '2055':
#                     logger.warning('数据库链接关闭，重新链接...')
#                     db.reconnect()
#                     db.savemany(r_list, table_name)
#                     print(''.join(['向',table_name, '存入', str(len(r_list)), '条数据！\n']))
#                 else:
#                     logger.info(str(r_list) + '存储出错：%s' % e)


def storage_process(db, q_storage_task, table_name, num=20):  # db链接到已定数据库
    while True:
        if not q_storage_task.empty():
            r = q_storage_task.get()
            if r is None:
                break
            storage(db, table_name, r)
        else:
            time.sleep(random.random())
        


def storage(db, table_name, values):
    try:
        db.save(values, table_name)
        print(values['URL'], '入库成功！')
    except Exception:
        n = 0
        while True:
            print(values['URL'], '存储时出错，5秒后重试...')
            time.sleep(5)
            try:
                db.save(values, table_name)
                print(values['URL'], '入库成功！')
            except Exception as e:
                if n >= 5:
                    logger.warning(str(values)+' 存储出错：%s' % str(e))
                    break
                n+=1
                continue
            else:
                break
