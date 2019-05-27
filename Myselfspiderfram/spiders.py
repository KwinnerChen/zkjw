#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


# 继承自BaseSpider，使用start_urls类变量时，必须实现response_parse方法，
# 定义类变量name
# 定义初始链接start_urls（列表），或者重新定义start_requests方法
# 对于回掉函数无需返回任务时可以直接返回None
# 返回任务对象在Commons.common.Task


from Commons.common import BaseSpider


class Spider(BaseSpider):
    pass

