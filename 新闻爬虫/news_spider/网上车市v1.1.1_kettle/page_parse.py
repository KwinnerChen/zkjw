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
        if 'xcjd' in response.url:
            urls, next_url = xcjd(tree)
        elif 'djbd' in response.url or 'fenxi' in response.url:
            urls, next_url = djbd_diaoyan(tree)
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        response.encoding = 'utf-8'
        tree = etree.HTML(response.text)
        current_url = response.url
        info_dict['URL'] = current_url
        title0 = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="border-box"]/h2/text()')))
        title1 = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="summary_title"]/h1/text()')))
        title2 = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="content"]//div[@class="cs_title"]/h1/text()')))
        if title0:
            info_dict['TITLE'] = title0
            info_parse_0(tree, info_dict)
        elif title1:
            info_dict['TITLE'] = title1
            info_parse_1(tree, info_dict)
        elif title2:
            info_dict['TITLE'] = title2
            info_parse_2(tree, info_dict)
        info_dict['COMMENTS_NUM'] = comments_num('http://comments.cheshi.com/new/?c=story&a=indexs&story_id=%s' % current_url.split('/')[-1].split('.')[0])
        info_dict['READ_NUM'] = ''
        info_dict['KEY_WORDS'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
        
    else:
        info_dict={}
    return info_dict


def comments_num(url):
    try:
        resp = page_downloader(url)
        html = resp.text
        tree = etree.HTML(html)
        comments_num = ''.join(tree.xpath('//div[@class="pl_title clearfix"]//a/span/text()'))
    except Exception:
        comments_num = '0'
    finally:
        return comments_num


def xcjd(tree):
    urls = tree.xpath('//dl[@class="clearfix zt_new"]/dt/a/@href')
    next_url_node = tree.xpath('//div[@class="pagebox"]//a')[-1]
    if next_url_node.xpath('.//@class') == 'current':
        next_url = None
    else:
        next_url = ''.join(next_url_node.xpath('.//@href'))
    return urls, next_url


def djbd_diaoyan(tree):
    urls = tree.xpath('//div[@class="listboxp bor"]//li//a/@href')
    next_url_node = tree.xpath('//div[@class="pagebox"]//a')[-1]
    if next_url_node.xpath('.//@class') == 'current':
        next_url = None
    else:
        next_url = ''.join(next_url_node.xpath('.//@href'))
    return urls, next_url
    
    
def info_parse_1(tree, info_dict):
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="status_new clearfix"]/a/text()'))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="summary_title"]//span[@id="pubtime_baidu"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="article"]//p/text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="article"]//img/@src')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="summary_title"]//span[@id="source_baidu"]//text()')))
        
        
def info_parse_2(tree, info_dict):
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="head_pub_news"]/p[@class="news_tit_pub"]//a/text()'))
    publish_time = re.search(r'[\d\- :]+', ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="cs_title"]/p/text()')))).group()
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="cs_content"]//p/text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="cs_content"]//img/@src')))
    data_source = re.search(r'来源：(\w+)', ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="cs_title"]/p/text()'))))
    info_dict['DATA_SOURCE'] = data_source.group(1) if data_source else '网上车市'
    
    
def info_parse_0(tree, info_dict):
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="breadcrumb"]/a/text()'))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_info"]//span[@class="fr"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="border-box"]//p/text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="border-box"]//img/@src')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_info"]//a/text()')))
