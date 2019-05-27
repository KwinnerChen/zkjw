#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import demjson
from lxml import etree
from urllib.parse import urljoin, urlsplit
from datetime import datetime
from downloader import page_downloader


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
def news_list_parse(response):
    if response:
        html = response.text
        current_url = response.url
        if 'token' not in current_url:
            tree = etree.HTML(html)
            token = get_token(response)
            if 'channel' not in current_url:
                urls = map(lambda x: urljoin('https://www.qctt.cn/news/', x), tree.xpath('//div[@class="part1 clearfix"]/div[@class="title"]/a/@href'))
                next_url = 'https://www.qctt.cn/loadmore?_token=%s&page=2' % token
            else:
                urls = map(lambda x: urljoin('https://www.qctt.cn/news/', x), tree.xpath('//div[@class="part1 clearfix"]/div[@class="title"]/a/@href'))
                next_url = 'https://www.qctt.cn/channel_loadmore/%s?_token=%s&page=2' % (current_url.split('/')[-1], token)
        else:
            if html:
                urls = map(lambda x: 'https://www.qctt.cn/news/'+str(x), ( i.get('id') for i in demjson.decode(html) if i))
            else:
                urls=[]
            cur_page_num = int(re.search(r'page=(\d+)', current_url).group(1))
            next_url = re.sub(r'page=\d+', 'page='+str(cur_page_num+1), current_url)
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        html = response.text
        tree = etree.HTML(html)
        current_url = response.url
        info_dict['URL'] = current_url
        info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="content_detail_left"]/div[@class="title"]/text()')))
        part2 = list(filter(None, (x.strip() for x in tree.xpath('//div[@class="content_detail_left"]/div[@class="part2"]//text()') if x)))
        if len(part2) == 4:
            info_dict['PUBLISH_TIME'] = datetime.strptime(part2[1], '%Y-%m-%d %H:%M:%S') 
            info_dict['READ_NUM'] = part2[-1]
            info_dict['DATA_SOURCE'] = '汽车头条'
        elif len(part2) == 5:
            info_dict['PUBLISH_TIME'] = datetime.strptime(part2[2], '%Y-%m-%d %H:%M:%S')
            info_dict['READ_NUM'] = part2[-1]
            info_dict['DATA_SOURCE'] = '汽车头条'
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="y_text2"]//p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="y_text2"]//img/@src')))
        info_dict['KEY_WORDS'] = ''
        info_dict['FLLJ'] = ''
        info_dict['COMMENTS_NUM'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
        return info_dict
    else:
        return {}
        

def get_token(response):
    # 首页token https://www.qctt.cn/home
    # 新车      https://www.qctt.cn/home/channel/0_1
    # 行业      https://www.qctt.cn/home/channel/0_2
    # 导购      https://www.qctt.cn/home/channel/0_3
    # 用车      https://www.qctt.cn/home/channel/0_30
    # 首页加载  https://www.qctt.cn/loadmore?_token=3Xj1gUe9JedjOu52YVsBIZ4tUiJNWr5j7H7qEk1D&page=2
    # 子栏目加载https://www.qctt.cn/channel_loadmore/0_1?_token=4nQVTgUgcs8NUmCgGYnktcHulYEnMYeV61vIRUCG&page=2&oldTime=2018-10-30+18:00:00
    # https://www.qctt.cn/channel_loadmore/0_1?_token=TNhfPI02xPMR1ovERBOMwlLkfqhSQyBsM9XYQ6aD&page=3&oldTime=2018-12-21+13:58:06
    html = response.text
    token = re.search(r'token ?= ?"(.*?)"', html)
    token = token.group(1) if token else ''
    return token

        
