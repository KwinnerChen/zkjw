#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import os


def parse(file_path):
    # 逐行读取文件内容
    # 行分割并处理为字典列表
    f_list = []
    f_dic = {}
    n=0
    f = open(file_path, 'r', encoding='utf-8')
    while True:
        s = f.readline()
        # 结尾前的文章放入列表
        # 并对字典初始化
        if s == '':
            f_list.append(f_dic)
            # print(f_dic)
            f_dic = {}
            break
        # 以第二个空格为标准，将之前的字典放入列表
        # 并对字典和计数器初始化
        elif s == '\n':
            n += 1
            if n == 2:
                f_list.append(f_dic)
                f_dic = {}
                n = 0
                # print(f_dic)
        # 将文章分割为字典
        else:
            l = s.split(':')
            f_dic[l[0]] = ''.join(l[1:])

    f.close()
    # print(f_list)
    return f_list


def filte(file_name, file_list, file1, file2, i, t):
    # 判断list中dict内容
    # 包含sinn字段的写入file1
    # 缺失sinn字段的写入file2
    for d in file_list:
        if 'ISSN' in d:
            file1.writelines([k+':'+v for k,v in d.items()])
            file1.write('\n')
            file1.write('\n')
            print(file_name, 'ISSN数据记录第 %s 条...' % i)
            i += 1
        if d and 'ISSN' not in d:
            file2.writelines([k+':'+v for k,v in d.items()])
            file2.write('\n')
            file2.write('\n')
            print(file_name, '无ISSN数据记录第 %s 条...' % t)
            t += 1


def run(file_with_sinn, file_without_sinn, n, t):
    # file_with_sinn, file_without_sinn不需要创建
    # 完整的包括扩展名的文本文件名

    file1 = open(file_with_sinn, 'a', encoding='utf-8')
    file2 = open(file_without_sinn, 'a', encoding='utf-8')

    for i in os.scandir():
        if os.path.isfile(i.path):
            continue
        for p in os.scandir(i):
            f_list = parse(p.path)
            filte(p.name, f_list, file1, file2, n, t)


if __name__ == '__main__':
    n = t = 1
    run('2018气侯汇总（with sinn）.txt', '2018气侯汇总（without sinn）.txt', n, t)
