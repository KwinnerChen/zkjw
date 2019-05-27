#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime


def news_list_parse(response):
    if response:
        response.encoding = response.apparent_encoding
        html = response.text
        tree = etree.HTML(html)
        title_list = tree.xpath('//ul[@class="article"]//h3/text()')
        url = map(lambda x: 'https:'+x, tree.xpath('//ul[@class="article"]/li/a/@href'))
        read_num = tree.xpath('//ul[@class="article"]//em[1]/text()')
        comments_id = tree.xpath('//ul[@class="article"]//em[2]/@data-articleid')
        next_url = urljoin(response.request.url, tree.xpath('//a[@class="page-item-next"]/@href')[0]) if tree.xpath('//a[@class="page-item-next"]/@href') else None
        list_tuple = zip(title_list, url, read_num, comments_id)
    else:
        list_tuple = []
        next_url = None
    return list_tuple, next_url
        

def news_info_parse(response, info_dict):
    if response:
        html = response.text
        tree = etree.HTML(html)
        try:
            publish_time = tree.xpath('//div[@class="article-info"]//span[@class="time"]/text()')[0].strip() if tree.xpath('//div[@class="article-info"]//span[@class="time"]/text()') else '2018年10月17日 09:00'
            content = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]//p/text()')))
            key_words = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="marks"]/child::a/text()')))
            img_url = ', '.join(map(lambda x: 'https:' + x, tree.xpath('//div[@id="articleContent"]//img/@src')))
            data_source = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="source"]/a/text()')))
            fllj = '/'.join(tree.xpath('//div[@class="breadnav fn-left"]//a/text()'))
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y年%m月%d日 %H:%M') if publish_time else datetime.now()
            info_dict['CONTENT'] = re.sub('\xa0', '', content)
            info_dict['KEY_WORDS'] = key_words
            info_dict['FLLJ'] = fllj
            info_dict['IMAGE_URL'] = img_url
            info_dict['DATA_SOURCE'] = data_source
            info_dict['CRAWLER_TIME'] = datetime.now()
        except:
            info_dict = None
    else:
        info_dict=None
    return info_dict
    
