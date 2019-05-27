#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from Commons.common import Task, BaseSpider
from selector import Selector
import json
import re

class GTNEWS(BaseSpider):
    name = 'gtxinwen'

    start_urls = [
        'http://www.gzrailway.com.cn/web/list/showcontentlist?parentId=16&pageNow=1',
        'http://www.gzrailway.com.cn/web/list/showcontentlist?parentId=18&pageNow=1'
    ]

    def get_bbs_info_list(self, response):
        if not response and response.status_code != 200:
            return Task()
        elif response.status_code == 200 and 'parentId=16' in response.url:
            js = response.text
            jl = json.loads(js)
            conlist = jl.get('conlist', [])
            pager = jl.get('pager',{})
            pagenow = pager.get('pageNow') or int(''.join(re.findall(r'pageNow=(\d+)', response.url)))-1
            totalpage = pager.get('totalPageCount') or int(''.join(re.findall(r'pageNow=(\d+)', response.url)))
            next_page = pagenow + 1
            news_task = [Task(url='http://www.gzrailway.com.cn/web/gtxw_d/%s'%i.get('id'), method='get', callback=self.content_parse) for i in conlist if i]
            list_task = Task(url='http://www.gzrailway.com.cn/web/list/showcontentlist?parentId=16&pageNow=%s'% next_page, method='get', callback=self.get_bbs_info_list) if pagenow<=totalpage else Task()
            print(news_task)
            print(list_task)
            return news_task, list_task
        elif response.status_code == 200 and 'parentId=18' in response.url:
            js = response.text
            jl = json.loads(js)
            conlist = jl.get('conlist', [])
            pager = jl.get('pager',{})
            pagenow = pager.get('pageNow') or int(''.join(re.findall(r'pageNow=(\d+)', response.url)))-1
            totalpage = pager.get('totalPageCount') or int(''.join(re.findall(r'pageNow=(\d+)', response.url)))
            next_page = pagenow + 1
            news_task = [Task(url='http://www.gzrailway.com.cn/web/tlyw_d/%s'%i.get('id'), method='get', callback=self.content_parse) for i in conlist if i]
            list_task = Task(url='http://www.gzrailway.com.cn/web/list/showcontentlist?parentId=18&pageNow=%s'% next_page, method='get', callback=self.get_bbs_info_list) if pagenow<=totalpage else Task()
            print(news_task)
            print(list_task)
            return news_task, list_task

    def content_parse(self, response):
        selector = Selector(response)
        title = ''.join(selector.xpath('//div[@class="web_content_title"]/text()'))
        publish_time = ''.join(selector.xpath('//div[@class="web_content_date"]/text()'))
        content1 = ''.join(i.strip() for i in selector.xpath('//div[@class="web_content_detail"]//p//text()') if i)
        content2 = ''.join(i.strip() for i in selector.xpath('//div[@class="web_content_detail"]//div//text()') if i)
        content = content1+content2
        content_html = selector.get_html('//div[@class="web_content_detail"]')
        section = ''.join(i.strip() for i in selector.xpath('//div[@class="address"]/a[3]/text()'))
        return Task(item=((None, title, content, content_html, publish_time, section, None),))

