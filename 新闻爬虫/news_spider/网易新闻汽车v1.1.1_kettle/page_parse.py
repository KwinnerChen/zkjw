#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
from lxml import etree
from urllib.parse import urljoin, unquote, urlsplit
from datetime import datetime


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
# 如无跟踪链接，需返回None，作为线程停止信号
def news_list_parse(response):
    if response:
        html = response.text
        urls = re.findall(r'"docurl":"([http|https].*?html)"', html)
        current_url = response.url
        current_page = re.search(r'cm_auto_?(\d+).js', current_url).group(1) if re.search(r'cm_auto_?(\d+).js', current_url) else 1
        next_url = re.sub(r'cm_auto_?(\d)*.js', 'cm_auto_0%s.js' % str(int(current_page)+1), current_url)
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        if 'auto' in response.url:
            html = response.text
            tree = etree.HTML(html)
            info_dict['URL'] = response.url
            info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="epContentLeft"]/h1/text()')))
            info_dict['FLLJ'] = ''.join(map(lambda x:x.strip(), tree.xpath('//div[@class="post_crumb"]//text()')))
            publish_time = re.search(r'[\d\- :]+', ''.join(tree.xpath('//div[@class="post_time_source"]/text()')))
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time.group().strip(), '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
            info_dict['KEY_WORDS'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="r tag"]//text()')))
            info_dict['IMAGE_URL'] = ', '.join(tree.xpath('//div[@id="endText"]//p/img/@src'))
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="endText"]//p/text()')))
            info_dict['DATA_SOURCE'] = '网易'
            info_dict['READ_NUM'] = ''
            info_dict['COMMENTS_NUM'] = ''
            info_dict['CRAWLER_TIME'] = datetime.now()
            # info_dict['read_num'] = ''.join(tree.xpath('//div[@class="l read-num"]/text()'))
            # info_dict['comments_num'] = ''.join(tree.xpath('//a[@class="comment-left-link"]/text()'))
            # print(info_dict['read_num'])
            # info_dict['read_num'] = re.search(r'\w+\((\d+)\)', ''.join(tree.xpath('//div[@class="l read-num"]/text()')))
        if 'dy' in response.url:
            tree = etree.HTML(response.text)
            info_dict['URL'] = response.url
            info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_title"]/h2/text()')))
            publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//p[@class="time"]/span[1]/text()')))
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d') if publish_time else datetime.now()
            info_dict['COMMENTS_NUM'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="share_box"]//span[@class="fr"]//a/text()')))
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_box"]//p/text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_box"]//p/img/@src')))
            info_dict['FLLJ'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="dy_logo"]/text()')))
            info_dict['DATA_SOURCE'] = '网易'
            info_dict['READ_NUM'] = ''
            info_dict['KEY_WORDS'] = ''
            info_dict['CRAWLER_TIME'] = datetime.now()
    else:
        info_dict={}
    return info_dict


# def dy_parse(response, info_dict):
#     tree = etree.HTML(response.text)
#     info_dict['url'] = response.url
#     info_dict['title'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_title"]/h2/text()')))
#     info_dict['publish_time'] = ''.join(map(lambda x: x.strip(), tree.xpath('//p[@class="time"]/span[1]/text()')))
#     info_dict['comments_num'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="share_box"]//span[@class="fr"]//a/text()')))
#     info_dict['content'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_box"]//p/text()')))
#     info_dict['image_url'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article_box"]//p/img/@src')))
#     info_dict['fllj'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="dy_logo"]/text()')))
#     info_dict['data_source'] = urlsplit(response.url).hostname
#     return info_dict
