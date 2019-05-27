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
        urls = tree.xpath('//div[@class="news_li"]//div[@class="news_nr"]/h2/a/@href')
        next_url = ''.join(tree.xpath('//div[@class="news_li"]//div[@class="p_page"]/a[@class="xy"][last()-1]/@href'))
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
        info_dict['FLLJ'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="dq_l"]//text()')))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="pjnr"]/h1[@id="newstitle"]/text()')))
        publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="lef"]/text()')))
        publish_time = re.search(r'\d+\-\d+\-\d+ \d+:\d+', publish_time).group() if re.search(r'\d+\-\d+\-\d+ \d+:\d+', publish_time) else ''
        info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
        data_source = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="lef"]/text()')))
        data_source = re.search(r'来源：(\w+)', data_source).group(1) if re.search(r'来源：(\w+)', data_source) else ''
        info_dict['DATA_SOURCE'] = data_source
        if '阅读全文' in html:
            all_parse(tree, current_url, info_dict)
        else:
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="show"]/p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="show"]//img/@src')))
        info_dict['READ_NUM'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['KEY_WORDS'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
    else:
        info_dict={}
    return info_dict


def all_parse(tree, current_url, info_dict):
    all_url = ''.join(tree.xpath('//div[@class="s_page"]//a[last()]/@href'))
    all_page = page_downloader(urljoin(current_url, all_url))
    if all_page:
        all_page.encoding = all_page.apparent_encoding
        html = all_page.text
        tree = etree.HTML(html)
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="show"]/p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="show"]//img/@src')))
    else:
        info_dict['CONTENT'] = ''
        info_dict['IMAGE_URL'] = ''