#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import json
from lxml import etree
from urllib.parse import urljoin, urlsplit
from datetime import datetime
from downloader import page_downloader


# 该方法需要返回一个跟踪链接，和一个新闻链接可迭代对象
# 无跟踪链接返回None不作为停止信号（以免列队之后还有可用链接而被终止）
def news_list_parse(response):
    if response:
        html = response.text
        tree = etree.HTML(html)
        urls = map(lambda x: urljoin(response.url, x), tree.xpath('//p[@class="tit blue"]/a/@href'))
        ne = ''.join(tree.xpath('//div[@class="pcauto_page"]//a[@class="next"]/@href'))
        next_url = urljoin(response.url, ne) if ne else None
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        response.encoding = response.apparent_encoding
        tree = etree.HTML(response.text)
        current_url = response.url
        info_dict['URL'] = current_url
        info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="pos-mark"]/a/text()'))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="artDes"]//h1//text()')))
        publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="pubTime"]/text()')))
        info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
        nofllow = tree.xpath('//div[class="pcauto_page"]//a[@rel="nofollow"]/@href')
        if nofllow:
            content, image_url = total_page(nofllow)
            info_dict['CONTENT'] = content
            info_dict['IMAGE_URL'] = image_url
        else:
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="artText clearfix"]/p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: urljoin(current_url, x.strip()), tree.xpath('//div[@class="artText clearfix"]//img/@src')))
        info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="artExc"]/p/a/text()')))
        info_dict['DATA_SOURCE'] = re.sub(r'来源[:： ]+', '', ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="ownner"]//text()'))))
        read_num, comments_num = get_comments_num(current_url)
        info_dict['READ_NUM'] = read_num
        info_dict['COMMENTS_NUM'] = comments_num
        info_dict['CRAWLER_TIME'] = datetime.now()
        return info_dict  
    else:
        info_dict={}
    return info_dict


def get_comments_num(current_url):
    base_url = 'https://cmt.pcauto.com.cn/action/topic/get_data.jsp?url=%s&callback=callbackFunc'
    resp = page_downloader(base_url % current_url[6:])
    if resp:
        read_num = re.search(r'"commentRelNum":(\d*)', resp.text)
        comments_num = re.search(r'"total":(\d*)', resp.text)
        read_num = read_num.group(1) if read_num else ''
        comments_num = comments_num.group(1) if comments_num else ''
    else:
        read_num = comments_num = ''
    return read_num, comments_num


def total_page(url):
    resp = page_downloader(url)
    if resp:
        resp.encoding = resp.apparent_encoding
        html = resp.text
        tree = etree.HTML(html)
        content = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="artText clearfix"]//text()')))
        image_url = ', '.join(map(lambda x: urljoin(url, x.strip()), tree.xpath('//div[@class="artText clearfix"]//img/@src')))
    else:
        content = image_url = ''
    return content, image_url
