#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/8/16 15:35
# @Author   : zequan.shao
# @File     : spiderRun.py
# @Software : PyCharm

from shuikeyuan02.spiders.SkySpider import SkySpider
# from shuikeyuan02.get_perio_key import perio_keys

import sys

# reload(sys)
#
# sys.setdefaultencoding('utf8')
from collections import OrderedDict
from mysql.connector import Connect
import json
import re
import time

import os
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


def china_in_string(strs):

    if strs:
        xx = re.sub("[A-Za-z0-9|_]", "", strs).strip()

        if xx:
            return True
        else:
            return False
    else:
        return False


def data_to_sql(conn, data):

    # 创建游标
    cursor = conn.cursor()

    sql = '''INSERT INTO sky_cont2017_1 VALUES (null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
    # sql2 = "INSERT INTO sky_auth VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    '''
    将传入的数据字典中需要存入数据库的字段存入数据库中！
    new_data_list 中存入的是关于期刊文章的数据。
    auth_list 中存入的是关于作者信息的数据。
    '''
    # auth_list = []
    new_data_list = []

    for d in data:

        new_data = OrderedDict()

        for k, v in d.items():
            if k == 'auth_detial' or k == 'page_range':
                continue

            new_data[k] = v

        new_data_list.append(new_data)

        # if d['auth_detial']:
        #     for auth in d['auth_detial']:

        #         auth_dict = OrderedDict()

        #         auth_dict['article_id'] = auth.get('article_id', None)
        #         auth_dict['authors_name'] = auth.get('authors_name', None)
        #         auth_dict['trans_authname'] = auth.get('trans_authname', None)
        #         auth_dict['unit_name'] = auth.get('unit_name', None)
        #         auth_dict['org_id'] = auth.get('org_id', None)
        #         auth_dict['org_name'] = auth.get('org_name', None)
        #         auth_dict['perio_id'] = auth.get('perio_id', None)
        #         auth_dict['record_id'] = auth.get('record_id', None)
        #         auth_dict['authors_seq'] = auth.get('authors_seq', None)
        #         auth_dict['id'] = auth.get('id', None)
        #         auth_dict['auth_area'] = ''

        #         for k in auth.keys():

        #             res = china_in_string(k)

        #             if res:
        #                 auth_dict['auth_area'] = k

        #         auth_list.append(auth_dict)

    try:
        for da in new_data_list:
            print('-----------------------------------------------------------------')
            try:
                print('数据类型%s, len%s' % (type(da), len(da)))
                print(da.values())
                cursor.execute(sql, list(da.values()))
                conn.commit()
            except Exception as e:
                print(e)
                cursor.close()
                print('cursor restart!')
                time.sleep(0.5)
                print('...')
                time.sleep(0.5)
                cursor = conn.cursor()
                time.sleep(0.5)
                print('...')
                time.sleep(0.5)
                print('cursor restart successfully!')
                cursor.execute(sql, list(da.values()))
    except Exception as e:
        print('Aticle data storage failed!')
        print (e)
        conn.rollback()

    # try:
    #     cursor.executemany(sql2, map(lambda x: x.values(), auth_list))
    #     conn.commit()
    #     print('data storage successed!')
    # except Exception as e:
    #     print('Author data storage failed!')
    #     print (e)
    #     conn.rollback()

    cursor.close()


if __name__ == '__main__':

    # key_list = [
        # 'whsldldxxb-yc','slghysj','zgslsdkxyjyxb','cjkxyyb','ggps','zgfxkh','slsdjs','zhih','rmzj','dbslsd','hhsl','sdzjdjs',
        # 'xbszyysgc','hbslsdxyxb','sltd','sstxzz','ynslfd','hnslsd','hensl','hbslsdjs',
        # 'jssl', 'gdslsd', 'jhslkj','bjsl','gxslsd', 'xsd', 'sljj','slsdkjjz', 'zgstbckx', 'slswzdh','shanxsl','jxslkj',
        # ]#perio_keys()

    # key_list = ['slxb','zhonggsl','ytgcxb','slfdxb','skxjz','nsyj','rmcj','rmhh','szybh','nsbdyslkj']
    key_list = ['sltd']
    spider = SkySpider('sky', '2017', '2017', '', '', *key_list)

    # start_request函数里面可以存放两个参数，一个是出错的期刊id，和出错的期刊页面数量
    for res in spider.start_request():

        for data in spider.parse(res):
            # print('准备存储...')
            # print(data)
            conn = Connect(user='root',password='1234',db='shuikeyuan')
            data_to_sql(conn, data)
            conn.close()

            time.sleep(1.5)
