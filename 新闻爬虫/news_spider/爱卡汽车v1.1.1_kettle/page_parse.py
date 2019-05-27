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
# 爱卡车站栏目需要cookie，改写downloader模块，使用session。
def news_list_parse(response):
    if response:
        current_url = response.url
        if 'chezhan' in current_url:
            if response.status_code == 201:
                # cookie = response.cookies.get_dict()
                resp = page_downloader(current_url)
                resp.encoding = resp.apparent_encoding
                tree = etree.HTML(resp.text)
            else:
                response.encoding = response.apparent_encoding
                tree = etree.HTML(response.text)
            urls = []
            next_url = ''.join(tree.xpath('//div[@class="hzcon1_center"]/h2/a/@href'))
        elif 'tag' in current_url:
            if response.status_code == 201:
                # cookie = response.cookies.get_dict()
                resp = page_downloader(current_url)
                resp.encoding = resp.apparent_encoding
                tree = etree.HTML(resp.text)
            else:
                response.encoding = response.apparent_encoding
                tree = etree.HTML(response.text)
            urls = tree.xpath('//a[@class="pag_public_a"]/@href')
            next_url = ''.join(tree.xpath('//div[@class="article_page_bottom"]/a[@id="page_next"]/@href'))
            next_url = urljoin(current_url, next_url) if 'html' in next_url else None
        else:
            response.encoding = response.apparent_encoding
            tree = etree.HTML(response.text)
            urls = tree.xpath('//dt[@class="listCon_title"]/a/@href')
            next_url = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_page_bottom"]/a[last()]/@href')))
            next_url = next_url if 'http' in next_url else None
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
        nextpage_span = tree.xpath('//div[@class="article_page_bottom page_v1"]')
        info_dict['URL'] = current_url
        info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="p1"]/a/text()')))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_title"]/h1/text()')))
        publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_info_span"]/span[@id="pubtime_baidu"]/text()')))
        info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
        info_dict['DATA_SOURCE'] = '爱卡汽车'
        info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//dd[@class="clearfix"]/span/a/text()')))
        info_dict['READ_NUM'] = ''.join(map(lambda x: x.strip(), tree.xpath('//a[@id="praise_bottom"]/i/text()')))
        info_dict['COMMENTS_NUM'] = ''.join(map(lambda x: x.strip(), tree.xpath('//a[@id="commentnumtwo"]/i/text()')))
        info_dict['CRAWLER_TIME'] = datetime.now()
        if nextpage_span:
            page_all_url = ''.join(map(lambda x: x.strip(), nextpage_span[0].xpath('.//a[@class="page_about_right"]/@href')))
            page_all_url = urljoin(current_url, page_all_url)
            all_page_info_parse(page_all_url, info_dict)
        else:
            info_parse(tree, info_dict)

    else:
        info_dict={}
    return info_dict


def all_page_info_parse(url, info_dict):
    resp = page_downloader(url)
    if resp:
        resp.encoding = resp.apparent_encoding
        html = resp.text
        tree = etree.HTML(html)
        info_parse(tree, info_dict)


def info_parse(tree, info_dict):
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="newsbody"]/p//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="newsbody"]//img/@src')))
         
