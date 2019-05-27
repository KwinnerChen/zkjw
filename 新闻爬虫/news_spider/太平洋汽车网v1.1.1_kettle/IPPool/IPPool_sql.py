#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python 3.6.4


import cx_Oracle
import json
import os
import random
import time


class IPPool():

    def __init__(self, user='beiqi', passsword='beiqi', host='123.57.7.118', port='1521', cid = 'orcl', db='BEIQI', table_name='PROXIES'):
        self.user = user
        self.passsword = passsword
        self.host = host
        self.port = port
        self.cid = cid
        self.db = db
        self.table_name = table_name

    def __refresh_ips(self):
        self.con = cx_Oracle.connect(self.user+'/'+self.passsword+'@'+self.host+':'+self.port+'/'+self.cid)
        self.cur = self.con.cursor()
        self.cur.execute('select * from %s.%s' % (self.db, self.table_name))
        result = self.cur.fetchall()
        ip_list = self.__parse_result(result)
        self.con.close()
        return ip_list

    def __parse_result(self, result):
        ip_list = []
        for t in result:
            ip_dict = {}
            v,k = t
            ip_dict[k] = k+'://'+v
            ip_list.append(ip_dict)
        return ip_list

    def __storage(self, slist):
        with open('proxies.json', 'w', encoding='utf-8') as f:
            json.dump(slist, f)

    def __get_ips_local(self):
        with open('proxies.json', 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    def get_ip(self):
        if os.path.exists('proxies.json') and os.path.getsize('proxies.json') > 300 and time.time()-os.path.getmtime('proxies.json') < 300:
            ip_list = self.__get_ips_local()
            # return random.choice(ip_list)
        else:
            while True:
                ip_list = self.__refresh_ips()
                if len(ip_list) < 20:
                    time.sleep(5)
                    continue
                self.__storage(ip_list)
                break
        return random.choice(ip_list)
  