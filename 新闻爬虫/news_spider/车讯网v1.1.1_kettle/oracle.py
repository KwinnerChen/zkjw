#! usr/bin/env python3
# -*- coding: utf-8 -*-


import cx_Oracle


class Oracle():
    def __init__(self, username, password, host):
        self.username = username
        self.password = password
        self.host = host
        self.con = cx_Oracle.connect(username, password, host)
        

    def savemany(self, table_name, values):
        sql = 'INSERT INTO {} VALUES(:TITLE, :CONTENT, :KEY_WORDS, :URL, :IMAGE_URL, :CLASS_TAG, :DATA_SOURCE, :READ_NUM, :COMMENTS_NUM, :PUBLISH_TIME, :CRAWLER_TIME)'.format(table_name)
        self.cur = self.con.cursor()
        self.cur.executmany(sql, values)
        self.con.commit()


    def save(self, table_name, value):
        sql = 'INSERT INTO {} VALUES(:TITLE, :CONTENT, :KEY_WORDS, :URL, :IMAGE_URL, :CLASS_TAG, :DATA_SOURCE, :READ_NUM, :COMMENTS_NUM, :PUBLISH_TIME, :CRAWLER_TIME)'.format(table_name)
        self.cur = self.con.cursor()
        self.cur.execut(sql, value)
        self.con.commit()


    def close(self):
        self.con.close()


    def reconnect(self):
        self.con = cx_Oracle.connect(self.username, self.password, self.host)
        self.cur = self.con.cursor()
