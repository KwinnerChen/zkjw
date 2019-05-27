#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


# 继承自BaseSpider，必须实现response_parse方法，
# 定义类变量name
# 定义初始链接start_urls（列表），或者重新定义start_requests方法


from Commons.common import BaseSpider
from Commons.common import Task
from Commons.common import TimeVerify
from Commons.common import Erro
from Commons.selector import Selector
from Commons.IPPool import IPPoolManager
from datetime import datetime
from urllib.parse import urljoin, unquote
import cx_Oracle
import config
import os
import re



# ORACLE口碑自增序列名KB_ID_SEQ
# 口碑印象自增序列KBIMPRESSION_ID_SEQ
# 车型数据表对应表自增序列CARID_ID_SEQ
# 插入时：INSERT INTO CRAW_KB(ID, USERNAME, ...) VALUES (KB_ID_SEQ.NEXTVAL, '用户', ...)
# 要17年之后的数据
# 使用了oracle自增序列，所以要改写一下存储模块
# KB_REAL_SEQ, IMPRESSION_REAL_SEQ
# 口碑移动网址https://k.m.autohome.com.cn/detail/view_01csvzrtq168s36e9g6rv00000.html


os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class Spider(BaseSpider):

    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }
    
    name = 'koubei_impression' 

    manager = IPPoolManager()
    ippool = manager.get_ippool()

    timeverifier = TimeVerify('2017-01-01', increment=0)  # 需要跨实例使用

    def start_request(self):
        base_url = 'https://k.autohome.com.cn/{TYPEID}/ge0/0-0-2/'
        con = cx_Oracle.connect('bq_data', 'tiger', '39.107.57.229:1521/orcl.lan')
        cur = con.cursor()
        cur.execute("SELECT CARTYPE, CARID FROM CRAW_KB_CARID2CARTYPE")
        carlist = cur.fetchall()
        cur.close()
        con.close()
        for i in carlist:
            url = base_url.format(TYPEID=i[1])
            cartype = i[0]
            yield Task(url=url, method='get', callback=self.yinxiang_parse, temp=cartype, headers=self.header, proxies=self.ippool.get())

    def yinxiang_parse(self, response, temp):
        if isinstance(response, Erro):  # 对于出现验证和下载失败的返回到任务列队重新下载
            return Task(url=response.url, method='get', callback=self.yinxiang_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        if 'safety' in response.url:
            url = response.url.split('=')[-1]
            url = urljoin('https://', unquote(url))
            print('%s 遇到验证，重新下载！'%url)
            return Task(url=url, method='get', callback=self.yinxiang_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        selector = Selector(response)
        # 帖子按推荐指数和时间排序，获取当页最新时间，不满足时间条件则结束函数，不再解析
        time_node = selector.xpath('//div[@class="title-name name-width-01"]//b/a/text()')
        root_nodes = selector.xpath('//div[@class="mouthcon"]')
        ltime = max(time_node)
        if not ltime or not time_node:
            print('%s 未解析到时间，重新下载！'%response.url)
            return Task(url=response.url, method='get', callback=self.yinxiang_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        if len(time_node)<15 and ltime<='2016-08-25' and temp not in ' '.join(i.strip() for i in root_nodes[0].xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "购买车型")]/dd//text()')):
            print('%s 获取到迷惑页面，重新下载！'%response.url)
            return Task(url=response.url, method='get', callback=self.yinxiang_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        if  not self.timeverifier.timeverify(temp, ltime):
            print('%s 日期超限！'%response.url)
            self.timeverifier.log_logpkl()
            return
        l = selector.xpath('//div[@class="revision-impress impress-small"]')
        if not l:
            print(temp, '暂无口碑数据！')
            item = {}
            item['IMPRESSION'] = '暂无'
            item['SCORE'] = None
            item['CARTYPE'] = temp
            item['CRAWLER_TIME'] = datetime.now()
            return Task(item=[item])
        l = l[0].xpath('./a/text()')
        # 评价
        pl = [re.split('[(（)）]', i)[0] for i in l if i]
        # 评价得分
        plf = [int(re.split('[(（)）]', i)[1]) for i in l if i]
        itemlist = []
        for i in zip(pl, plf):
            item = {}
            item['IMPRESSION'] = i[0]
            item['SCORE'] = i[1]
            item['CARTYPE'] = temp
            item['CRAWLER_TIME'] = datetime.now()
            itemlist.append(item)
        return Task(item=itemlist)

    