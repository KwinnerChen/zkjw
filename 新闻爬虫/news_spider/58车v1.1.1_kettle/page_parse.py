#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


# import re
# import demjson
from lxml import etree
from urllib.parse import urljoin #, unquote, urlsplit
from datetime import datetime
from downloader import page_downloader


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
def news_list_parse(response):
    if response:
        current_url = response.url
        response.encoding = response.apparent_encoding
        tree = etree.HTML(response.text)
        urls1 = tree.xpath('//ul[@class="zx-newscon1"]/li/a/@href')
        urls2 = tree.xpath('//div[@class="zx-newscon2"]//h3/a/@href')
        urls = urls1 + urls2
        urls = map(lambda x: urljoin(current_url, x), urls) if urls else []
        next_url = ''.join(tree.xpath('//a[@class="next"]/@href'))
        next_url = urljoin(current_url, ''.join(tree.xpath('//a[@class="next"]/@href'))) if next_url else None
        
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        response.encoding = response.apparent_encoding
        html = response.text
        tree = etree.HTML(html)
        current_url = response.url
        info_dict['URL'] = current_url
        info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="head-mbx l"]/a/text()')))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//h1[@class="h_title"]/text()')))
        publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="a_t l"]/span[1]/text()')))
        info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
        info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="a_t l"]/span[2]/a/text()')))
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="c_tcon clearfix"]/p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="c_tcon clearfix"]//img/@src')))
        info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//dl[@class="news_tag clearfix"]//a/text()')))
        info_dict['READ_NUM'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
        
    else:
        info_dict={}
    return info_dict


