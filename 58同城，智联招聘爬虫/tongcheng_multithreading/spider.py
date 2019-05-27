#! usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
import config
import json
from IPPool.IPPool import IPPool
from storage import DB
from downloader import page_downloader, RetryErro
from page_parse import parse_total_page, get_url_jobinfo, jobinfo_parse
from multiprocessing import Process, Queue
from threading import Thread


def log_url(logname):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)
    handler = logging.FileHandler(logname, encoding='utf-8')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(message)s')
    handler.setFormatter(fmt=formatter)
    logger.addHandler(handler)
    return logger


def get_total_page(area, site, keyword, logger, q_proxiy):
    SEARCH_URL = 'https://{0}.58.com/{1}job/?key={2}&final=1&jump=1'
    try:
        html_total = page_downloader(SEARCH_URL.format(area, site, keyword), flags='search', proxiy=q_proxiy)
    except RetryErro as e:
        print(SEARCH_URL.format(area, site, keyword), e, ' 无法继续解析，已记录到log_url.txt中。\n')
        logger.info(SEARCH_URL.format(area, site, keyword)+' 下载失败\n')
        return None
    else:
        total_page = parse_total_page(html_total)
        print(area, site, keyword, '共', total_page, '页\n')
        if not total_page:
            print(SEARCH_URL.format(area, site, keyword), ' 解析为空，无法继续，记入log_url.txt。\n')
            logger.info(SEARCH_URL.format(area, site, keyword)+' 下载失败\n')
        return total_page


def proxiy_pool(ippool, q_proxiy):  # 向代理列队添加代理ip，单独一个进程
    while True:
        if not q_proxiy.full():
            proxy = ippool.get_ip
            q_proxiy.put(proxy)
            # print('put', proxy, 'in q_proxiy。')


def worker(area, site, keyword, q_proxiy, q_result, logger):  # 主要工作线程，返回值为字典列表，添加到结果列队
    BASE_URL = 'https://{0}.58.com/{1}job/pn{2}/?key={3}&final=1&jump=1'
    total_page = get_total_page(area, site, keyword, logger, q_proxiy)
    if total_page:
        for n in range(1, total_page+1):
            result_list = []
            print('下载 ', BASE_URL.format(area, site, n, keyword))
            html_url = page_downloader(BASE_URL.format(area, site, n, keyword), flags='page', proxiy=q_proxiy)
            if not html_url:
                print(BASE_URL.format(area, site, n, keyword), ' 下载失败，记入log_url.txt。\n')
                logger.info(BASE_URL.format(area, site, n, keyword) + ' 下载失败\n')
            else:
                print('解析 ', BASE_URL.format(area, site, n, keyword))
                job_urls = get_url_jobinfo(html_url)
                if job_urls:
                    for u in job_urls:
                        print('下载 ', u)
                        html = page_downloader(u, flags='page', proxiy=q_proxiy)
                        if html:
                            print('解析 ', u)
                            result = jobinfo_parse(area, html)
                            if result and result.get('job_id', ''):
                                print(result)
                                result_list.append(result)
                            else:
                                print(u, '解析失败，记入log_url.txt\n')
                                logger.info(u + '解析失败\n')
                        else:
                            print(u, '下载失败，记入log_url.txt。\n')
                            logger.info(u+' 下载失败\n')
                    q_result.put(result_list)
                else:
                    print(BASE_URL.format(area, site, n, keyword), '解析失败，记入log_url.txt。\n')
                    logger.info(BASE_URL.format(area, site, n, keyword)+' 解析失败\n')
        else:
            logger.info(''.join([area, ' ', site, ' ', keyword, ' 爬取完毕。\n']))
    else:
        logger.info(''.join([area, ' ', site, ' ', keyword, ' 没有抓取到页数。\n']))


def thread_worker(area, sites, q_task, q_proxiy, q_result, logger):
    while True:
        if not q_task.empty():
            keyword = q_task.get()
            if keyword is None:
                break
            for site in sites:
                worker(area, site, keyword, q_proxiy, q_result, logger)


def thread_maker(area, sites, q_task, q_proxiy, q_result, logger, task_thread_num, thread_worker, thread_list):
    for n in range(task_thread_num):
        t = Thread(target=thread_worker, args=(area, sites, q_task, q_proxiy, q_result, logger) )
        t.start()
        thread_list.append(t)  # 将创建的线程加入线程列表


def storage_wrong_log(s):
    with open(config.STORAGE_LOG, 'a', encoding='utf-8') as f:
        f.write(s)


def storage_process(db, table_name, q_result):
    while True:
        if not q_result.empty():
            result = q_result.get()
            if result is None:
                print('关闭数据库。')
                db.close()
                break
            try:
                db.savemany(result, table_name)
                print('存储', len(result), '条。\n')
            except Exception as e:
                print(result, '存储出错:', e)
                storage_wrong_log(str(result)+'存储出错！')
                continue
            