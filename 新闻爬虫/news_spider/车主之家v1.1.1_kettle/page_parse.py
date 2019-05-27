#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import demjson
from lxml import etree
from urllib.parse import urljoin, unquote, urlsplit
from datetime import datetime
from downloader import page_downloader


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
def news_list_parse(response):
    if response:
        html = response.text
        current_url = response.url
        tree = etree.HTML(html)
        urls = tree.xpath('//div[@class="news_list"]//li/a[2]/@href')
        part_next_url = ''.join(tree.xpath('//div[@class="page"]/a[last()][@class]/@href'))
        if part_next_url:
            next_url = urljoin(current_url, part_next_url)
        else:
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
        if '在本页阅读全文' in html:
            resp = page_downloader(re.sub(r'\.html', '_all.html', response.url))
            resp.encoding = resp.apparent_encoding
            html = resp.text
        tree = etree.HTML(html)
        current_url = response.url
        info_dict['URL'] = current_url
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news_title"]/text()')))
        part2 = list(filter(None, (x.strip() for x in tree.xpath('//div[@class="news_admin"]//text()') if x)))
        info_dict['PUBLISH_TIME'] = datetime.strptime(part2[0], '%Y年%m月%d日 %H:%M') if part2 else datetime.now()
        # info_dict['read_num'] = part2[-1]
        data_source = re.search(r'来源：(.*)', part2[1], flags=re.DOTALL)
        info_dict['DATA_SOURCE'] = data_source.group(1).strip() if data_source else ''
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="news_content"]//p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="news_content"]//img/@src')))
        info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="web_site"]/a/text()')))
        info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="new_related"]/h2//a/text()')))
        info_dict['READ_NUM'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
        return info_dict
    else:
        return {}
        

        