#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import os
from hashlib import md5
from collections import OrderedDict


def parse(file_path, true_set):
    # 逐行读取文件内容
    # 将文本转换为字典列表
    # 字典hash编码set()判断是否存在
    # 结果转换为真假值列表
    file_dic = OrderedDict()
    file_list = []
    true_list = []
    n=0
    f = open(file_path, 'r', encoding='utf-8')
    while True:
        s = f.readline()
        # 判断文档终点
        if s == '':
            break
        # 以第二个空格为标准，将之前的字典放入列表
        # 并对字典和计数器初始化
        elif s == '\n':
            n += 1
            if n == 2:
                file_list.append(file_dic)
                m = md5(str(file_dic).encode('utf-8')).hexdigest()
                print(file_dic['题名'], '编码为', m)
                if m not in true_set:
                    print(file_dic['题名'], '无重复！')
                    true_list.append(True)
                    true_set.add(m)
                else:
                    print(file_dic['题名'], '已存在！')
                    true_list.append(False)
                file_dic = OrderedDict()
                n = 0
        # 将文档块分割为字典
        else:
            l = s.split(':')
            file_dic[l[0]] = ''.join(l[1:])

    f.close()
    del file_dic
    return file_list, true_list


def filte(file_list, true_list):
    # 将重复元素筛选出
    l_true = (i[0] for i in zip(file_list, true_list) if i[1])
    l_false = (i[0] for i in zip(file_list, true_list) if not i[1])
    return l_true, l_false


def save(l, file_name):
    # 将字典列表写入文件
    with open(file_name, 'w', encoding='utf-8') as file:
        n = 0
        for i in l:
            file.writelines((k+':'+v for k,v in i.items()))
            file.write('\n')
            file.write('\n')
            n += 1
        print(file_name, '写入', n, '条！')


def run(file_path, true_set, file_name1, file_name2):
    file_list, true_list = parse(file_path, true_set)
    l_true, l_false = filte(file_list, true_list)
    save(l_true, file_name1)
    save(l_false, file_name2)


if __name__ == '__main__':
    true_set = set()
    file_path = '/home/kkchen/桌面/气象/2018气候-处理后/2018气侯汇总（with sinn）.txt'
    file_name1 = '2018年气候数据汇总送审.txt'
    file_name2 = '删除重复数据记录.txt'
    run(file_path, true_set, file_name1, file_name2)
