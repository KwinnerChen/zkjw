#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/10/8 11:23
# @Author   : zequan.shao
# @File     : SqlOption.py
# @Software : PyCharm

import time
import cx_Oracle


class SqlOption:

    def __init__(self, host, user, passwd, SID='ORCL'):
        if not host:
            raise ValueError('The value of host is None, it must have value.')
        if not user:
            raise ValueError('The value of user is None, it must have value.')
        if not passwd:
            raise ValueError('The value of passwd is None, it must have value.')

        self.host = host + '/' + SID
        self.user = user
        self.passwd = passwd
        self.conn = None
        self.cursor = None

    def connection(self):
        try:
            self.conn = cx_Oracle.connect(self.user, self.passwd, self.host)
            self.cursor = self.conn.cursor()
        except Exception:
            time.sleep(3)
            self.connection()

    def close(self):
        if not self.conn:
            raise ValueError('The connection is invalid.')
        if not self.cursor:
            raise ValueError('The cursor is invalid.')

        self.cursor.close()
        self.conn.close()

    def update_option(self, sql, data):
        self.cursor.execute(sql, data)
        self.conn.commit()

    def insert_option(self, sql, data):
        self.cursor.execute(sql, data)
        self.conn.commit()

    def remove_option(self, sql, data):
        self.cursor.execute(sql, data)
        self.conn.commit()

    def insert_many(self, data):
        sql = '''INSERT INTO PROXIES VALUES(:IP,:AGREEMENT)'''
        self.cursor.executemany(sql, data)
        self.conn.commit()

    def truncate_option(self):
        self.cursor.execute('truncate table PROXIES')
        self.conn.commit()
