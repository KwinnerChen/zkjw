#! usr/bin/env python3
# -*- coding: utf-8 -*-

try:
    from mysql.connector import Connect
except ImportError:
    from pymysql import Connect


class DB():
    def __init__(self, **kwargs):
        self.con = Connect(**kwargs)
        self.cur = self.con.cursor()


    def save(self, info_dict, table_name):
        data = self.__data_parser(info_dict)
        sql_insert = '''INSERT INTO {0} VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, null)'''.format(table_name)
        self.cur.execute(sql_insert, data)  # 之后改成executemany，节省资源 
        self.con.commit()


    def savemany(self, infodict_list, table_name):
        sql_insert = '''INSERT INTO {0} VALUES (null, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, null)'''.format(table_name)
        datas = self.__datalist_parser(infodict_list)
        self.cur.executemany(sql_insert, datas)
        self.con.commit()


    def __datalist_parser(self, infodict_list):
        al = []
        for info_dict in infodict_list:
            al.append(self.__data_parser(info_dict))
        return al


    def __data_parser(self, info_dict):
        data = (
            info_dict.get("job_id", "").encode('utf-8'),
            info_dict.get("job_bt", "").encode('utf-8'),
            info_dict.get("job_yx", "").encode('utf-8'),
            info_dict.get("job_gznx", "").encode('utf-8'),
            info_dict.get("job_rs", "").encode('utf-8'),
            info_dict.get("job_zpdd", "").encode('utf-8'),
            info_dict.get("job_xz", "").encode('utf-8'),
            info_dict.get("job_xl", "").encode('utf-8'),
            info_dict.get("job_zwlb", "").encode('utf-8'),
            info_dict.get("job_zwms", "").encode('utf-8'),
            info_dict.get("job_company", "").encode('utf-8'),
            info_dict.get("job_gsmc", "").encode('utf-8'),
            info_dict.get("job_gsgm", "").encode('utf-8'),
            info_dict.get("job_gsxz", "").encode('utf-8'),
            info_dict.get("job_gshy", "").encode('utf-8'),
            info_dict.get("job_gsdz", "").encode('utf-8'),
            info_dict.get("job_gszy", "").encode('utf-8'),
            info_dict.get("hybq", "").encode('utf-8'),
            info_dict.get("job_gsfl1", "").encode('utf-8'),
            info_dict.get("job_gsfl2", "").encode('utf-8'),
            info_dict.get("job_gsfl3", "").encode('utf-8'),
            info_dict.get("job_gsfl4", "").encode('utf-8'),
            info_dict.get("job_gsfl5", "").encode('utf-8'),
            info_dict.get("job_gsfl6", "").encode('utf-8'),
            info_dict.get("job_gsfl7", "").encode('utf-8'),
            info_dict.get("job_gsfl8", "").encode('utf-8'),
            info_dict.get("job_gsfl9", "").encode('utf-8'),
            info_dict.get("job_gsfl10", "").encode('utf-8'),
            info_dict.get("data_source", "").encode('utf-8'),
            info_dict.get("job_fbsj", "2018-01-01").encode('utf-8')
            )
        return data


    def close(self):
        self.con.close()