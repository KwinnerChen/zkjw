#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


from turn2xml import TOXML
import xlrd
import pymysql


if __name__ == '__main__':

    test = TOXML()
    con = pymysql.connect(user='root', password='1234', db='shuikeyuan')
    cur = con.cursor()
    cur.execute('select * from sky_cont2017_1')

    while True:
        data = cur.fetchone()
        if data is None:  # 读取完毕后退出
            con.close()
            break
        try:
            struct = {
                'METADATAS':{
                    'METADATA':{
                        'DOCTITLE':data[9],
                        'CRUSER':'admin',
                        'CRTIME':'2018-10-19 11:19:17.0',
                        'CRNUMBER':'201',
                        'DOCCHANNELID':'15409552362809096',
                        'DOCSTATUS':'10',
                        'SITEID':'15394818974643478',
                        'OPERTIME':'2018-10-19 11:19:17.0',
                        'DOCRELTIME':'2018-10-19 11:19:17.0',
                        'WENZM':data[9],
                        'ZUOZHE':data[22],
                        'ZHAIYAO':data[7],
                        'GJC':data[2],
                        'NJQ':data[16],
                        'STARTPAGE':data[25],
                        'ENDPAGE':data[26],
                        'DOI':data[11],
                        'QWADD':data[21],
                        'YEMA':data[19],
                        'DOWNLOADSHU':data[14],
                        'NIANQI':data[15],
                        'ABSTRACT':data[8][:1500],
                        'KEYWORDS':data[3],
                        'SSQK':data[5],
                        'SGRQ':''
                    }
                }
            }
            # file_name = data[9]
            # 不可以用文章标题做文件名，因为文章标题不规范，含有文件名禁止字符。
            file_path = '.\\sky\\'
            test.turn2xml(struct)
            print(data[9], '转换为xml...')
            test.storage(file_path=file_path)
            print(data[9], '存储于', file_path)
        except Exception as e:
            print(e)
            input()
            continue
