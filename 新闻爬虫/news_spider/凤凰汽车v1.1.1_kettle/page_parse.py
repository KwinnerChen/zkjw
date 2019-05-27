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
        html = response.content.decode('utf-8')
        current_url = response.url
        tree = etree.HTML(html)
        if 'zhuanlan' not in current_url:
            next_url_part = ''.join(tree.xpath('//div[@class="v2c-page"]/a[@class="next"]/@href'))
            next_url = urljoin(current_url, next_url_part) if next_url_part else None
            urls = tree.xpath('//div[@class="v2c-lst-li"]/a[@class="tit"]/@href')
        else:
            print('开始解析专栏链接, 用时稍长...')
            urls = zhuanlan_urls(tree)
            print('专栏链接解析完毕！')
            next_url = None
    else:
        urls = []
        next_url = None
    return urls, next_url
    

# 该方法解析新闻详情页面，返回一个字典，如无内容返回一个空字典。
def news_info_parse(response, info_dict):
    if response:
        html = response.content.decode('utf-8')
        tree = etree.HTML(html)
        current_url = response.url
        info_dict['URL'] = current_url
        if 'zhuanlan' not in current_url:
            if '阅读全文' in html:
                all_url = urljoin(current_url, ''.join(tree.xpath('//div[@class="arl-pages"]/a[@class="full"]/@href')))
                resp = page_downloader(all_url)
                tree = etree.HTML(resp.content.decode('utf-8'))
            news_parse(current_url, tree, info_dict)
            info_dict['READ_NUM'] = ''
            info_dict['COMMENTS_NUM'] = ''
            info_dict['CRAWLER_TIME'] = datetime.now()
        else:
            zhuanlan_parse(current_url, tree, info_dict)
            info_dict['CRAWLER_TIME'] = datetime.now()
    else:
        info_dict={}
    return info_dict


def zhuanlan_urls(tree):
    zhuanlan_urls = tree.xpath('//div[@class="ct-author-tit"]/a/@href')
    urls = []
    for url in zhuanlan_urls:
        print('解析%s' % url)
        resp = page_downloader(url)
        if resp:
            html = resp.content.decode('utf-8')
            tree = etree.HTML(html)
            url_list = tree.xpath('//div[@class="item"]/h3/a/@href')
            if url_list:
                for u in url_list:
                    urls.append(u)
                print('解析完成 %s，文章链接 %s 条。' % (url, len(url_list)))
    return urls


def news_parse(current_url, tree, info_dict):
    info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="t-cur"]//a/text()')))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="arl-cont"]/h3//text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="d1"]/span[@id="pubtime_baidu"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y年%m月%d日 %H:%M:%S') if publish_time else datetime.now()
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="d2"]/span[@id="source_baidu"]/a/text()')))
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="arl-c-txt"]/p//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="arl-c-txt"]//img/@src')))
    # info_dict['comments_num'] = get_comments_num(response)
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="alst"]//text()'))) 


def zhuanlan_parse(current_url, tree, info_dict):
    info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="w-crumbNav"]//a/text()')))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical"]/h1[@id="artical_topic"]/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical_sth"]/p/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y年%m月%d日 %H:%M:%S') if publish_time else datetime.now()
    info_dict['DATA_SOURCE'] = '凤凰汽车行业专栏'
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical_real"]/div[@id="artical_real"]/p//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical_real"]/div[@id="artical_real"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical_sth2"]/a/text()'))) 
    next_page = tree.xpath('//div[@class="pageNum"]/child::*')
    if next_page:
        child_page_num = len(next_page)
        for i in range(1, child_page_num):
            next_page_url = urljoin(current_url, ''.join(map(lambda x: x.strip(), next_page[i].xpath('./@href')))) 
            resp = page_downloader(next_page_url)
            if resp:
                tree = etree.HTML(resp.content.decode('utf-8'))
                info_dict['CONTENT'] = ''.join([info_dict['content'], ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical_real"]/div[@id="artical_real"]/p//text()')))])
                info_dict['IMAGE_URL'] = ', '.join([info_dict['image_url'], ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artical_real"]/div[@id="artical_real"]//img/@src')))])
    read_num, comments_num = get_zhuanlan_num(current_url)
    info_dict['READ_NUM'] = read_num
    info_dict['COMMENTS_NUM'] = comments_num


def get_zhuanlan_num(current_url):
    url = 'https://comment.ifeng.com/joincount.php?doc_url=' + current_url.replace('https', 'http')
    resp = page_downloader(url)
    if resp:
        string = resp.text
        num_list = re.findall(r'\d+', string)
        if num_list:
            return num_list[1], num_list[0]
        else:
            return 0, 0
    else:
        return 0, 0