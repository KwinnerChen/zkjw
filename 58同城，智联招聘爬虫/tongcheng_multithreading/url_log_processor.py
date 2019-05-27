#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: 3.6.4


import os
import json
import requests
import random
import re
import redis
from downloader import page_downloader
from page_parse import get_url_jobinfo, jobinfo_parse, parse_total_page
# from tongcheng_multithreading import get_url_jobinfo, page_download, jobinfo_parse
# from tongcheng import ippool, USER_AGENT
# from urllib.parse import urlsplit
# from lxml.etree import HTML


# 去重文件地址（用于内存去重）
# SET_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '\\url_set.json')

URL_LOG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '\\url_log2.txt')


class UrlList():

    # FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)) + '\\url_log.txt')
    FILE_PATH = r'.\url_log.txt'

    def __init__(self):
        self.file = open(self.FILE_PATH, encoding='utf-8')     

    def get_url(self):
        contentL = self.file.readlines()
        m = map(lambda x: re.search(r'(https?://.*?)[下载失败解析]+', x).group(1), contentL)
        return m

    def close(self):
        self.file.close()
        

# 使用redis数据库去重
class Url_Filter():
    def __init__(self):
        self.con_pool = redis.ConnectionPool()
        self.con = redis.Redis(connection_pool=self.con_pool)

    def sadd(self, name, *value):
        return self.con.sadd(name, *value)


def log_url(url, path):
    with open(path, 'a', encoding='utf-8') as f:
        f.write(url+'下载失败\n')


def jobinfo_url_processer(url, area, proxiy):
    html = page_downloader(url, flags='page', proxiy=proxiy)
    if html:
        rd = jobinfo_parse(area, html)
    else:
        rd = None
    return rd


def joburl_processor(url, area, proxiy):
    html = page_downloader(url, flags='search', proxiy=proxiy)
    if html:
        job_urls = get_url_jobinfo(html)
    else:
        job_urls = None
    return job_urls


def process(url, area, url_filter, set_name, proxiy, log_path):
    if url_filter.sadd(set_name, url):
        if len(url) > 60: 
            rd = jobinfo_url_processer(url, area, proxiy)
            if rd:
                # return rd
                print(rd)
            else:
                log_url(url, log_path)
        else:
            job_urls = joburl_processor(url, area, proxiy)
            if job_urls:
                for ju in job_urls:
                    if url_filter.sadd(set_name, ju):
                        rd = jobinfo_url_processer(ju, area, proxiy)
                        if rd:
                            # return rd
                            print(rd)
                        else:
                            log_url(ju, log_path)
                    else:
                        print(ju, '重复，此链接已处理...')
            else:
                log_url(url, log_path)
    else:
        print(url, '重复， 此链接已处理...')


if __name__ == '__main__':
    pass