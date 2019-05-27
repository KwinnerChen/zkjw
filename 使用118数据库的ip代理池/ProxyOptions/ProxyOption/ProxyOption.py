#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/9/19 11:58
# @Author   : zequan.shao
# @File     : ProxyOption.py
# @Software : PyCharm

import re
import requests
from scrapy import Selector


class ProxyOption:

    def __init__(self, url, header):
        if not url:
            raise ValueError('The url is None.')

        self.url = url
        self.header = header
        print('代理地址：', self.url)

    # 请求代理api地址
    def _request_proxy(self):
        return requests.get(self.url, headers=self.header) if self.header else requests.get(self.url)

    # 解析页面，返回代理ip列表
    def _get_proxy(self, response):
        if response.status_code == 200:
            res = Selector(text=response.content)
            ip_list = res.xpath('/html/body/text()').extract()
            if ip_list:
                return [ip for ip in map(lambda x: x.strip(), ip_list) if ip]

    # 验证代理是否可用
    def _verify_proxy(self, proxy):
        try:
            response = requests.get('https://www.baidu.com/',
                                    proxies={'https': 'https://' + proxy}, timeout=3)
            return True if response.status_code == 200 else False
        except Exception:
            return False

    # 将可用的代理ip存入代理池中
    def push_proxy(self, lock=None):
        '''
        将可用的ip代理放入队列中
        :param queue: 存放代理ip
        :return:
        '''
        print('||')
        print('||')
        print('插入代理池开始...')
        ip_list = self._parse_regular(self._request_proxy())
        if ip_list:
            if lock:
                lock.acquire()
            ip_count = 0
            with open('./ProxyOption/proxies.txt', 'w') as fp:
                for ip in ip_list:
                #if self._verify_proxy(ip):
                    ip_count += 1
                    fp.write(ip + '\n')
            print('Insert to ip pool, number is %s' % ip_count)
            if lock:
                lock.release()
        else:
            print('Do not get ip from web.')

    # 更新代理池
    def update_proxy(self, lock=None):
        print('||')
        print('||')
        print('更新代理池开始...')
        try:
            with open('./ProxyOption/proxies.txt', 'r') as fp1:
                new_ip_list = [line for line in fp1.readlines()] #if self._verify_proxy(line.strip())]
            if lock:
                lock.acquire()
            print('After update ip pool, the left ip number is %s' % len(new_ip_list))
            with open('./ProxyOption/proxies.txt', 'w') as fp2:
                if new_ip_list:
                    for ip in new_ip_list:
                        fp2.write(ip)
                else:
                    fp2.write('')
            if lock:
                lock.release()
        except FileNotFoundError:
            print('Not found file,please wait a moment.')

    def _parse_regular(self, response):
        '''
        通过正则的方式来解析页面
        :param response: 请求页面返回的对象
        :return:
        '''

        if response.status_code == 200:
            return re.findall('[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}:[\d]{1,7}', response.text)
