#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/9/12 16:06
# @Author   : zequan.shao
# @File     : run.py
# @Software : PyCharm

import threading

import sys

sys.path.append(r'F:\zkjw\code\zhilianNoScrapy\zhilianSpider\spiders')
sys.path.append(r'F:\zkjw\code\zhilianNoScrapy\zhilianSpider\SqlOptions')

from spiders import ZLSpider


if __name__ == '__main__':

    spider = ZLSpider.ZLSpider()

    keywords = [
        # 'hr','医药代表','策划','市场营销','市场专员',
        # '数据挖掘','自然语言处理','算法工程师',
        # '家政服务员','养老护理员','育婴员','美容师','美发师','美甲师',
        # '仓库管理','仓储','库房',
        # '销售','行政',
        '医药代表','策划','市场营销','市场专员','出纳','会计','财务',
    ] 

    # api进程
    api_threads = []
    for keyword in keywords:
        one_thread = threading.Thread(target=spider.get_data_from_api, args=(keyword, ))
        api_threads.append(one_thread)

    # 详情页面进程
    detial_threads = []
    for ke in range(3):
        two_thread = threading.Thread(target=spider.engin_detial)
        detial_threads.append(two_thread)

    three_thread = threading.Thread(target=spider.data_storage)

    for one_thread in api_threads:
        one_thread.start()

    for two_thread in detial_threads:
        two_thread.start()

    three_thread.start()

    for one_thread in api_threads:
        one_thread.join()

    for two_thread in detial_threads:
        two_thread.join()

    three_thread.join()
