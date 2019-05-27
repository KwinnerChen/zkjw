#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import requests
from lxml import etree
from datetime import datetime


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
def news_list_parse(response):
    if response:
        response.encoding = response.apparent_encoding
        html = response.text
        tree = etree.HTML(html)
        urls1 = tree.xpath('//ul[@class="carKbList"]//p/a/@href')
        urls2 = tree.xpath('//ol[@class="carfabuTex"]/li//a/@href')
        urls = urls1+urls2
        next_url = None
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
        info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="navigatev1New"]//a/text()')))
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="w662 conclewrap"]/h1/text()')))
        publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="w662 conclewrap"]/p[@class="coninfo"]/text()[1]')))
        info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
        data_source = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="w662 conclewrap"]/p[@class="coninfo"]/span[1]/text()')))
        info_dict['DATA_SOURCE'] = data_source
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="conBox plr37"]/p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="conBox plr37"]//img/@src')))
        info_dict['READ_NUM'] = get_read_num(current_url)
        info_dict['KEY_WORDS'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
    else:
        info_dict={}
    return info_dict


def get_read_num(current_url):
    headers = {
        'Host': 'www.chekb.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
    }
    Id = current_url.split('/')[-1].split('_')[0]
    resp = requests.get('http://www.chekb.com/tools/view.php?archiveId=%s' % Id, headers=headers)
    html = resp.text
    num = re.search(r'\d+', html)
    if num:
        return num.group()
    else:
        return '0'




