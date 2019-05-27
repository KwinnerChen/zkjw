#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import json
from lxml import etree
from urllib.parse import urljoin, unquote, urlsplit
from datetime import datetime
from downloader import page_downloader


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
def news_list_parse(response):
    if response:
        html = response.text
        tree = etree.HTML(html)
        urls = map(lambda x: urljoin(response.url, x), tree.xpath('//div[@class="body"]/ul[@id="LIST_LM"]/li/div[@class="newTxt"]/h3/a/@href'))
        next_url = None
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        html = response.text
        tree = etree.HTML(html)
        current_url = response.url
        info_dict['URL'] = current_url
        title_info_node1 = tree.xpath('//div[@class="a_Info"]') 
        title_info_node2 = tree.xpath('//div[@class="ll"]')
        if title_info_node1:
            info_dict['FLLJ'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="a_Info"]//span[@class="a_catalog"]/a/text()')))
            publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="a_Info"]//span[@class="a_time"]/text()')))
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
            info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="a_Info"]//span[@class="a_source"]//text()')))
        elif title_info_node2:
            info_dict['FLLJ'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="ll"]//span[@class="color-a-0"]/a/text()')))
            publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="ll"]//span[@class="article-time"]/text()')))
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
            info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="ll"]//span[@class="color-a-1"]//text()')))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="hd"]/h1/text()')))
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="bd"]/div[@id="Cnt-Main-Article-QQ"]/p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="bd"]/div[@id="Cnt-Main-Article-QQ"]/p//img/@src')))
        info_dict['READ_NUM'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['KEY_WORDS'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
    else:
        info_dict={}
    return info_dict

