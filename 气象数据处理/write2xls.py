#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v3.6.6


import xlwt
from check_issn import parse

class XLS():
    def __init__(self):
        self.book = xlwt.Workbook()
        self.sheet = self.book.add_sheet('sheet1')
        self.sheet.write(0, 0, label='题名')
        self.sheet.write(0, 1, label='子分类')
        self.sheet.write(0, 2, label='分类号')
        self.sheet.write(0, 3, label='作者')
        self.sheet.write(0, 4, label='关键词')
        self.sheet.write(0, 5, label='单位')
        self.sheet.write(0, 6, label='摘要')
        self.sheet.write(0, 7, label='刊名')
        self.sheet.write(0, 8, label='ISSN')
        self.sheet.write(0, 9, label='年')
        self.sheet.write(0, 10, label='期')
        self.sheet.write(0, 11, label='第一责任人')

    def write(self, dict_list):
        for i in range(len(dict_list)):
            flh = dict_list[i].get('分类号', '')
            self.sheet.write(i+1, 0, label=dict_list[i].get('题名'))
            self.sheet.write(i+1, 1, label=dict_list[i].get('子分类'))
            self.sheet.write(i+1, 2, label=flh if '（' not in flh else flh.split('（')[1][:-2])
            self.sheet.write(i+1, 3, label=dict_list[i].get('作者'))
            self.sheet.write(i+1, 4, label=dict_list[i].get('关键词'))
            self.sheet.write(i+1, 5, label=dict_list[i].get('单位'))
            self.sheet.write(i+1, 6, label=dict_list[i].get('摘要'))
            self.sheet.write(i+1, 7, label=dict_list[i].get('刊名'))
            self.sheet.write(i+1, 8, label=dict_list[i].get('ISSN'))
            self.sheet.write(i+1, 9, label=dict_list[i].get('年'))
            self.sheet.write(i+1, 10, label=dict_list[i].get('期'))
            self.sheet.write(i+1, 11, label=dict_list[i].get('第一责任人'))

    def save(self, file_name):
        self.book.save(file_name)


if __name__ == '__main__':
    xls = XLS()
    file_path = '.\\2018年气候数据汇总送审.txt'
    dict_list = parse(file_path)
    xls.write(dict_list)
    xls.save('可导入数据格式.xls')
    print('完成！')
