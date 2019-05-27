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
        urls = tree.xpath('//main[@id="main"]//header/h2/a/@href')
        next_url = ''.join(tree.xpath('//div[@class="nav-links"]/span[@class="next"]/a/@href'))
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
        info_dict['FLLJ'] = ''.join(map(lambda x: x.strip(), tree.xpath('//nav[@class="breadcrumb"]//text()')))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//header[@class="entry-header"]/h1/text()')))
        publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="single-cat-tag"]/div[@class="single-cat"]/text()')))
        publish_time = re.search(r'\d+年\d+月\d+日', publish_time).group() if '年' in publish_time else ''
        publish_time = datetime.strptime(publish_time, '%Y年%m月%d日') if publish_time else datetime.now()
        info_dict['PUBLISH_TIME'] = publish_time
        info_dict['DATA_SOURCE'] = '汽车探索网'
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="single-content"]/p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="single-content"]//img/@src')))
        info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="single-tag"]//text()')))
        info_dict['READ_NUM'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
    else:
        info_dict={}
    return info_dict

