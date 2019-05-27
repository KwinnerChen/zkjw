#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import json
from lxml import etree
from urllib.parse import urljoin, unquote, urlsplit
from datetime import datetime


def news_list_parse(response):
    if response:
        html = response.text
        callback = re.search(r'jQuery[\d_]+\((.*?)\);', html).group(1)
        json1 = json.loads(callback)
        if json1:
            # title = map(lambda x: x['title'], json1)
            url = list(map(lambda x: 'http://www.sohu.com/a/'+str(x['id'])+'_'+str(x['authorId']), json1))
            # http://v2.sohu.com/public-api/feed?scene=CHANNEL&sceneId=18&page=30&size=20&callback=jQuery1124048264666558010483_1540289206668
            list_tuple = url
            current_pagenum = int(re.search(r'page=(\d+)', response.url).group(1))
            next_url = re.sub(r'page=\d+', 'page=%s' % str(current_pagenum+1), response.url)
        else:
            list_tuple = []
            next_url = None
    else:
        list_tuple = []
        next_url = None
    return list_tuple, next_url
    

def news_info_parse(response, info_dict):
    if response:
        html = response.text
        tree = etree.HTML(html)
        info_dict['URL'] = response.url
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//h3[@class="article-title"]/text()')))
        info_dict['FLLJ'] = ''.join(map(lambda x:x.strip(), tree.xpath('//div[@class="location area"]//text()')))
        publish_time = ''.join(tree.xpath('//span[@class="l time"]/text()'))
        info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
        info_dict['KEY_WORDS'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="r tag"]//text()')))
        info_dict['IMAGE_URL'] = ', '.join(tree.xpath('//article[@class="article-text"]//img/@data-src'))
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//article[@class="article-text"]//text()')))
        info_dict['DATA_SOURCE'] = '搜狐'
        read_num = ''.join(tree.xpath('//div[@class="l read-num"]/text()'))
        read_num_n = ''.join(re.findall(r'阅读[(（]([\d\w\.]+)[)）]', read_num)) if read_num else read_num
        read_num_n = read_num_n if '万' not in read_num_n else str(int(float(read_num_n.replace('万', ''))*10000))
        info_dict['READ_NUM'] = read_num_n
        info_dict['COMMENTS_NUM'] = ''.join(tree.xpath('//a[@class="comment-left-link"]/text()'))
        info_dict['CRAWLER_TIME'] = datetime.now()
        # print(info_dict['read_num'])
        # info_dict['read_num'] = re.search(r'\w+\((\d+)\)', ''.join(tree.xpath('//div[@class="l read-num"]/text()')))
    else:
        info_dict={}
    return info_dict

