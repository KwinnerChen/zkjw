#! usr/bin/env python3
# -*- coding: utf-8 -*-

import config
import requests
import random
import time
from urllib.parse import urlsplit


class RetryErro(Exception):
    def __str__(self):
        return '已达到重试次数!'


class VerifyErro(Exception):
    def __str__(self):
        return '本次访问需要验证!'


def page_downloader(url, flags, proxiy, retry=config.RETRY):  # proxiy是一个ip列队，flags取值为search和page
    headers = {
        'User-Agent': random.choice(config.USER_AGENT),
        # 'Host': urlsplit(url).netloc,
    }
    n = 0
    while True:
        try:
            time.sleep(random.random()*4)
            proxiy_ip = proxiy.get()
            if flags == 'search':
                resp = requests.get(url, headers=headers, proxies=proxiy_ip, timeout=3)
            if flags == 'page':
                resp = requests.get(url, headers=headers, proxies=proxiy_ip, timeout=3)
            resp.raise_for_status
            html = resp.text
            if '访问过于频繁' in html:  # 验证码待处理
                input(url + ' 需要验证，请处理后任意键重试...')
                continue
        except Exception as e:
            if n < retry:
                print(url, ' ', e, ' 重试...\n')
                n = n+1
                continue
            else:
                html = None
        return html

