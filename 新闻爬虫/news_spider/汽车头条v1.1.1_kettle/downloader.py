#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


# news_list_url = ''


# import config
import requests
import random
import time
from urllib.parse import urlsplit


def page_downloader(url, proxiy=None, agent_pool=None, delay=None, timeout=None, retry=3):  # proxiy是一个ip列队
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0' if agent_pool is None else random.choice(agent_pool),
        'Host': urlsplit(url).hostname,
        'TE': 'Trailers',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    n = 0
    while True:
        try:
            if delay:
                time.sleep(delay)
            # print(type(proxiy))
            proxiy_ip = None if proxiy is None else proxiy.get()
            # print(proxiy_ip)
            resp = requests.get(url, headers=headers, proxies=proxiy_ip, timeout=timeout)
            resp.raise_for_status
            if '访问过于频繁' in resp.text:  # 验证码待处理
                input(url + ' 需要验证，请处理后任意键重试...\n')
                continue
        except Exception as e:
            n += 1
            if n < retry:
                print(url, ' ', e, ' 重试...\n')
                continue
            else:
                resp = None
        return resp

