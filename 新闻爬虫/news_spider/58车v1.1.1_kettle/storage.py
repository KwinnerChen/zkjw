#! usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from mysql.connector import Connect
except ImportError:
    from pymysql import Connect
import cx_Oracle


class DB():
    def __init__(self, **kwargs):
        self.con = Connect(**kwargs)
        self.cur = self.con.cursor()
        self.kwargs = kwargs


    def save(self, info_dict, table_name):
        data = self.__data_parser(info_dict)
        sql_insert = '''INSERT INTO {0} VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,null)'''.format(table_name)
        self.cur.execute(sql_insert, data)  # 之后改成executemany，节省资源 
        self.con.commit()

    def savemany(self, infodict_list, table_name):
        sql_insert = '''INSERT INTO {0} VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, null)'''.format(table_name)
        datas = self.__datalist_parser(infodict_list)
        self.cur.executemany(sql_insert, datas)
        self.con.commit()

    def reconnect(self):
        self.con = Connect(**self.kwargs)
        self.cur = self.con.cursor()

    def __datalist_parser(self, infodict_list):
        al = []
        for info_dict in infodict_list:
            al.append(self.__data_parser(info_dict))
        return al


    def __data_parser(self, info_dict):
        data = (
            info_dict.get("title", "").encode('utf-8'),
            info_dict.get("content", "").encode('utf-8'),
            info_dict.get("key_words", "").encode('utf-8'),
            info_dict.get("url", "").encode('utf-8'),
            info_dict.get("image_url", "").encode('utf-8'),
            info_dict.get("fllj", "").encode('utf-8'),
            info_dict.get("data_source", "").encode('utf-8'),
            info_dict.get("read_num", "").encode('utf-8'),
            info_dict.get("comments_num", "").encode('utf-8'),
            info_dict.get("publish_time", "").encode('utf-8'),
            )
        return data


    def close(self):
        self.con.close()


class Oracle():
    def __init__(self, username, password, host):
        self.username = username
        self.password = password
        self.host = host
        self.conpool = cx_Oracle.SessionPool(username, password, host)
        

    def savemany(self, values, table_name):
        sql = '''INSERT INTO {}(TITLE, KEY_WORDS, URL, IMAGE_URL, FLLJ, DATA_SOURCE, READ_NUM, COMMENTS_NUM, PUBLISH_TIME, CRAWLER_TIME, CONTENT) VALUES(:TITLE, :KEY_WORDS, :URL, :IMAGE_URL, :FLLJ, :DATA_SOURCE, :READ_NUM, :COMMENTS_NUM, :PUBLISH_TIME, :CRAWLER_TIME, :CONTENT)'''.format(table_name)
        self.con = self.conpool.acquire()
        self.cur = self.con.cursor()
        self.cur.executemany(sql, values)
        self.con.commit()
        self.cur.close()
        self.conpool.release(self.con)


    def save(self, value, table_name):
        sql = '''INSERT INTO {}(TITLE, KEY_WORDS, URL, IMAGE_URL, FLLJ, DATA_SOURCE, READ_NUM, COMMENTS_NUM, PUBLISH_TIME, CRAWLER_TIME, CONTENT) VALUES(:TITLE, :KEY_WORDS, :URL, :IMAGE_URL, :FLLJ, :DATA_SOURCE, :READ_NUM, :COMMENTS_NUM, :PUBLISH_TIME, :CRAWLER_TIME, :CONTENT)'''.format(table_name)
        self.con = self.conpool.acquire()
        self.cur = self.con.cursor()
        self.cur.execute(sql, value)
        self.con.commit()
        self.cur.close()
        self.conpool.release(self.con)


    def close(self):
        self.con.close()

