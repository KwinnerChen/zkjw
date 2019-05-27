#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v 3.6.4


import cx_Oracle
from collections import OrderedDict


class Oracle():
    def __init__(self, user, password, host):
        self.user = user
        self.password = password
        self.host = host
        self.conpool = cx_Oracle.SessionPool(user, password, host)

    # 表不存在创建，存在不做反应
    def try_to_create_table(self, table_name, data_struct):
        con = self.conpool.acquire()
        cur = con.cursor()
        sql = 'CREATE TABLE %s(%s)' % (table_name, ', '.join(map(lambda x: x[0] + ' ' + x[1], data_struct.items())))
        try:
            cur.execute(sql)
        except Exception as e:
            if 'ORA-00955' in str(e):
                pass
            else:
                raise ValueError('创建表失败！%s' % e)
        else:
            con.commit()
        cur.close()
        self.conpool.release(con)

    def save(self, table_name, data_struct, value):
        # data_struct是一个字典
        con = self.conpool.acquire()
        cur = con.cursor()
        or_d = OrderedDict(data_struct) # 绑定变量有序
        sql = 'INSERT INTO %s(%s) VALUES(%s)' % (table_name, ','.join(or_d.keys()), ','.join(map(lambda x: ':'+x, or_d.keys())))
        cur.execute(sql, value)
        con.commit()
        cur.close()
        self.conpool.release(con)

    def savemany(self, table_name, data_struct, values):
        con = self.conpool.acquire()
        cur = con.cursor()
        or_d = OrderedDict(data_struct)
        sql = 'INSERT INTO %s(%s) VALUES(%s)' % (table_name, ','.join(or_d.keys()), ','.join(map(lambda x: ':'+x, or_d.keys())))
        cur.executemany(sql, values)
        con.commit()
        cur.close()
        self.conpool.release(con)

    def reconnect(self):
        self.conpool = cx_Oracle.SessionPool(self.user, self.password, self.host)

    def getall(self, table_name, *args, **kwargs):
        con = self.conpool.acquire()
        cur = con.cursor()
        if not args:
            if not kwargs:
                sql = 'SELECT %s FROM %s' % ('*', table_name)
            elif len(kwargs) > 1:
                sql = 'SELECT %s FROM %s WHERE %s' % ('*', table_name, ' AND '.join(map(lambda x: x[0]+'='+x[1], kwargs.items())))
            elif len(kwargs) == 1:
                sql = 'SELECT %s FROM %s WHERE %s' % ('*', table_name, ' = '.join(kwargs.items()))
        elif len(args) > 1:
            if not kwargs:
                sql = 'SELECT %s FROM %s' % (', '.join(args))
            elif len(kwargs) > 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (', '.join(args), table_name, ' AND '.join(map(lambda x: x[0]+'='+x[1], kwargs.items())))
            elif len(kwargs) == 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (', '.join(args), table_name, ' = '.join(kwargs.items()))
        elif len(args) == 1:
            if not kwargs:
                sql = 'SELECT %s FROM %s' % (args[0])
            elif len(kwargs) > 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (args[0], table_name, ' AND '.join(map(lambda x: x[0]+'='+x[1], kwargs.items())))
            elif len(kwargs) == 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (args[0], table_name, ' = '.join(kwargs.items()))
        cur.execute(sql)
        data = cur.fetchall()
        cur.close()
        self.conpool.release(con)
        return data

    def getmany(self, table_name, num, *args, **kwargs):
        con = self.conpool.acquire()
        cur = con.cursor()
        if not args:
            if not kwargs:
                sql = 'SELECT %s FROM %s' % ('*', table_name)
            elif len(kwargs) > 1:
                sql = 'SELECT %s FROM %s WHERE %s' % ('*', table_name, ' AND '.join(map(lambda x: x[0]+'='+x[1], kwargs.items())))
            elif len(kwargs) == 1:
                sql = 'SELECT %s FROM %s WHERE %s' % ('*', table_name, ' = '.join(kwargs.items()))
        elif len(args) > 1:
            if not kwargs:
                sql = 'SELECT %s FROM %s' % (', '.join(args))
            elif len(kwargs) > 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (', '.join(args), table_name, ' AND '.join(map(lambda x: x[0]+'='+x[1], kwargs.items())))
            elif len(kwargs) == 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (', '.join(args), table_name, ' = '.join(kwargs.items()))
        elif len(args) == 1:
            if not kwargs:
                sql = 'SELECT %s FROM %s' % (args[0])
            elif len(kwargs) > 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (args[0], table_name, ' AND '.join(map(lambda x: x[0]+'='+x[1], kwargs.items())))
            elif len(kwargs) == 1:
                sql = 'SELECT %s FROM %s WHERE %s' % (args[0], table_name, ' = '.join(kwargs.items()))
        cur.execute(sql)
        data = cur.fetchmany(num)
        cur.close()
        self.conpool.release(con)
        return data


    def close(self):
        try:
            self.conpool.close()
        except:
            pass


