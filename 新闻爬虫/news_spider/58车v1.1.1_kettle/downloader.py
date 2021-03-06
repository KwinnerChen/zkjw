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


def page_downloader(url, proxiy=None, agent_pool=None, delay=None, timeout=5, retry=3, **kwargs):  # proxiy是一个ip列队
    headers = {
        'User-Agent': 'Mozilla/5.0' if agent_pool is None else random.choice(agent_pool),
        'Host': urlsplit(url).hostname,
    }
    n = 0
    while True:
        try:
            if delay:
                time.sleep(delay)
            # print(type(proxiy))
            proxiy_ip = None if proxiy is None else proxiy.get()
            # print(proxiy_ip)
            resp = Session_d.get(url, headers=headers, proxies=proxiy_ip, timeout=timeout, **kwargs)
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


class Session_d:
    session = requests.Session()

    @classmethod
    def get(cls, url, **kwargs):
        return cls.session.get(url, **kwargs)

    @classmethod
    def post(cls, url, **kwargs):
        return cls.session.post(url, **kwargs)