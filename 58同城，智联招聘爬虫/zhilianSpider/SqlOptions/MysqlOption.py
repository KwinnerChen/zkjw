#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/9/12 15:34
# @Author   : zequan.shao
# @File     : MysqlOption.py
# @Software : PyCharm

try:
    import MySQLdb
except ImportError:
    from mysql import connector as MySQLdb
import os
import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
sys.path.append(os.path.abspath(os.path.dirname(__file__)))


class MysqlOption:

    host = 'localhost'
    port = 3306
    user = 'root'
    passwd = '1234'
    db = 'job_info'
    charset = 'utf8'

    def __init__(self):

        self.data_insert_list = []

        self.conn = ''
        self.cursor = ''

    # 链接数据库
    def connection_to_sql(self):

        self.conn = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db,
                                    charset=self.charset)

        self.cursor = self.conn.cursor()

    # 插入操作
    def insert_option(self, data_dict):

        sql = "INSERT INTO zhilian VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        data_tup = (data_dict['job_id'].encode('utf-8'), data_dict['job_bt'].encode('utf-8'), data_dict['job_yx'].encode('utf-8'), data_dict['job_gznx'].encode('utf-8'), data_dict['job_rs'].encode('utf-8'), data_dict['job_zpdd'].encode('utf-8'), data_dict['job_xz'].encode('utf-8'), data_dict['job_xl'].encode('utf-8')
                    , data_dict['job_zwlb'].encode('utf-8'), data_dict['job_zwms'].encode('utf-8'), data_dict['job_company'].encode('utf-8'), data_dict['job_gsmc'].encode('utf-8'), data_dict['job_gsgm'].encode('utf-8'), data_dict['job_gsxz'].encode('utf-8'), data_dict['job_gshy'].encode('utf-8'), data_dict['job_gsdz'].encode('utf-8')
                    , data_dict['job_gszy'].encode('utf-8'), data_dict['hybq'].encode('utf-8'), data_dict['job_gsfl1'].encode('utf-8'), data_dict['job_gsfl2'].encode('utf-8'), data_dict['job_gsfl3'].encode('utf-8'), data_dict['job_gsfl4'].encode('utf-8'), data_dict['job_gsfl5'].encode('utf-8'), data_dict['job_gsfl6'].encode('utf-8')
                    , data_dict['job_gsfl7'].encode('utf-8'), data_dict['job_gsfl8'].encode('utf-8'), data_dict['job_fbsj'].encode('utf-8'), data_dict['data_source'].encode('utf-8'), data_dict['crawer_time'].encode('utf-8'))

        self.data_insert_list.append(data_tup)

        # print len(self.data_insert_list)

        if len(self.data_insert_list) >= 25:

            try:
                self.connection_to_sql()

            except Exception as e:

                print(e)
                print(u'数据库链接错误！')

            try:

                print(self.data_insert_list)

                self.cursor.executemany(sql, self.data_insert_list)
                self.conn.commit()

                del self.data_insert_list[:]

            except Exception as e:

                print(e)
                print(u'数据库存入出错！')
                self.conn.rollback()

                # 保留错误数据，以备后续需要。
                if not os.path.exists('./WrongData'):
                    os.makedirs('./WrongData')

                with open('./WrongData/data.txt', 'a+') as fp:

                    for i in self.data_insert_list:
                        i = str(i)
                        fp.write(i+'\n')

                del self.data_insert_list[:]

            finally:
                self.close_sql()

    # 数据库关闭
    def close_sql(self):

        self.cursor.close()
        self.conn.close()