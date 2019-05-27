#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v 3.6.4


import pkuseg as pkg
from os import path


class Filter():

    key_words = {
        '豪华SVIP',
        '豪华款',
        '豪华版',
        '豪华大床',
        '豪华阵容',
        '豪华新阵容',
        '豪华套餐',
        '豪华奖励',
        '豪华晚餐',
        '豪华大餐',
        '豪华午餐',
        '豪华舞美',
        '豪华明星',
        '豪华套房',
        '豪华游艇',
        '豪华游轮',
        '豪华包间',
        '豪华工作餐',
        '豪华泳池',
        '豪华外卖',
        '豪华早餐',
        '豪华酒店',
        '豪华的舞台',
        '豪华厂商',
        '豪华幼儿园',
        '豪华品牌',
        '豪华车型',
        '豪华汽车',
        '豪华大巴',
        '豪华三明治',
        '豪华螺蛳粉',
        '豪华间',
        '豪华房',
        '豪华礼包',
        '豪华车',
        '豪华奖励',
        '豪华的办公室',
        '豪华演员',
        '豪华煎饼',
        '豪华商店',
        '豪华电脑',
        '豪华包间',
    }

    def __init__(self, model='ctb8', user_dict=[]):
        self.filter = pkg.pkuseg(model_name=model, user_dict=user_dict)

    def set_model_dict(self, model='ctb8', user_dict=[]):
        self.filter = pkg.pkuseg(model_name=model, user_dict=user_dict)

    def cut(self, text):
        return self.filter.cut(text)

    def file_keyword(self, txt):
        cut_set = set(self.cut(txt))
        result = False
        if cut_set&self.key_words:
            result = True
        return result


if __name__ == '__main__':
    my_dict = ['豪华SVIP',
        '豪华款',
        '豪华版',
        '豪华大床',
        '豪华阵容',
        '豪华新阵容',
        '豪华套餐',
        '豪华奖励',
        '豪华晚餐',
        '豪华大餐',
        '豪华午餐',
        '豪华舞美',
        '豪华明星',
        '豪华套房',
        '豪华游艇',
        '豪华游轮',
        '豪华包间',
        '豪华工作餐',
        '豪华泳池',
        '豪华外卖',
        '豪华早餐',
        '豪华酒店',
        '豪华的舞台',
        '豪华厂商',
        '豪华幼儿园',
        '豪华品牌',
        '豪华车型',
        '豪华汽车',
        '豪华大巴',
        '豪华三明治',
        '豪华螺蛳粉',
        '豪华间',
        '豪华房',
        '豪华礼包',
        '豪华车',
        '豪华奖励',
        '豪华的办公室',
        '豪华演员',
        '豪华煎饼',
        '豪华商店',
        '豪华电脑',
        '豪华包间',]
    seg = Filter(user_dict=my_dict)
    # seg.set_model_dict(user_dict=my_dict)
    f = open('user_info.txt', 'r', encoding='utf-8')
    line = f.readline()
    while line:
        print('处理%s' % line)
        user_dict = eval(line.strip())
        post_text = user_dict.get('user_post_texts', '')
        result = seg.file_keyword(post_text)
        if result:
            print('包含过滤词')
            with open('filted_true.txt', 'a', encoding='utf-8') as fp:
                fp.write(line)
        else:
            print('未包含过滤词')
            with open('filter_false.txt', 'a', encoding='utf-8') as fp:
                fp.write(line)
        line = f.readline()
    f.close()


        
    