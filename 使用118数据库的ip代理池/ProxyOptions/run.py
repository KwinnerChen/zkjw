#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/10/8 11:43
# @Author   : zequan.shao
# @File     : run.py
# @Software : PyCharm

import time

from SqlOptions.SqlOption import SqlOption
from ProxyOption.ProxyOption import ProxyOption
from multiprocessing import Process, Lock

HOST = '123.57.7.118'
USER = 'beiqi'
PASSWD = 'beiqi'


def proxy_to_sql(ora):
    '''
    :param ora: SqlOption 实例对象
    :return:
    '''
    while True:
        ip_list = []
        try:
            fp = open('./ProxyOption/proxies.txt', 'r')
            for ip in fp.readlines():
                ip_dict = {}
                print('ip: %s' % ip)
                if ip.strip():
                    ip_dict['IP'] = ip.strip()
                    ip_dict['AGREEMENT'] = 'https'
                    ip_list.append(ip_dict)
            print('ip lenth: %s ' % len(ip_list))
            fp.close()
            if not ip_list:
                print('The ip file is None, please wait a moment.')
                time.sleep(10)
                continue
            ora.connection()
            ora.truncate_option()
            ora.insert_many(ip_list)
            ora.close()
        except FileNotFoundError:
            print('Do not find file, please wait a moment.')
            time.sleep(10)
            continue

        time.sleep(30)


def proxy_option(func, lock, sec=360):
    while True:
        func(lock)
        time.sleep(sec)


if __name__ == '__main__':

    lock = Lock()
    ip_url = 'http://vip22.xiguadaili.com/ip/?tid=556082430314945&num=2000&category=2&protocol=https'
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }

    ora = SqlOption(host=HOST, user=USER, passwd=PASSWD)
    pro = ProxyOption(ip_url, header)

    get_proxy_process = Process(target=proxy_option, args=(pro.push_proxy, lock))
    update_proxy_process = Process(target=proxy_option, args=(pro.update_proxy, lock, 150))
    sql_process = Process(target=proxy_to_sql, args=(ora,))

    get_proxy_process.start()
    time.sleep(2)
    update_proxy_process.start()
    time.sleep(5)
    sql_process.start()

    get_proxy_process.join()
    update_proxy_process.join()
    sql_process.join()

