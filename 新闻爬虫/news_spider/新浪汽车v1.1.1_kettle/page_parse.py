#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import re
import json
import requests
import time
from lxml import etree
from urllib.parse import urljoin, unquote, urlsplit
from datetime import datetime


# 该方法需要返回一个跟踪链接，和一个新闻链接列表
# 如无跟踪链接，需返回None，作为线程停止信号
def news_list_parse(response):
    if response:
        html = response.text
        r = ''.join(re.findall(r'jQuery[\d_]+\((.*)\)', html))
        try:
            j = json.loads(r)
        except:
            j = {}
        if j.get('msg', '') == 'succ':
            html = j.get('data', '')
            if isinstance(html, str):
                tree = etree.HTML(html)
                urls = tree.xpath('//div[@class="s-left fL clearfix"]/h3/a/@href')
                current_url = response.url
                current_page = re.search(r'page=(\d+)', current_url).group(1) if re.search(r'page=(\d+)', current_url) else 1
                next_url = re.sub(r'page=(\d+)', 'page=%s' % str(int(current_page)+1), current_url)
            else:
                urls = []
                next_url = None
        else:
            urls = []
            next_url = None
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
        if '/f/' in current_url and 'ihmuuiyv' in current_url:
            info_dict = ihmuuiyv_parse(tree, current_url, info_dict)
        elif '/hy/' in current_url and 'ihmutuec' in current_url:
            info_dict = hy_ihmutuec_parse(tree, current_url, info_dict)
        elif '/hy/' in current_url and 'ifxeuwws' in current_url:
            info_dict = hy_ifxeuwws_parse(tree, current_url, info_dict)
        elif '/ct/' in current_url and 'ifyhwefp' in current_url:
            info_dict = ct_ifyhwefp_parse(tree, current_url, info_dict)
        elif '/ct/' in current_url and 'ifyeceza' in current_url:
            info_dict = ct_ifyhwefp_parse(tree, current_url, info_dict)
        elif '/f/' in current_url and 'ifynhhay' in current_url:
            info_dict = ct_ifyhwefp_parse(tree, current_url, info_dict)
        elif '/f/' in current_url and 'ifymkwwk' in current_url:
            info_dict = ct_ifyhwefp_parse(tree, current_url, info_dict)
        elif '/f/' in current_url and 'ifxeuwws' in current_url:
            info_dict = ihmuuiyv_parse(tree, current_url, info_dict)
        elif '/ct/' in current_url:
            info_dict = ct_parse(tree, current_url, info_dict)
        elif '/f/' in current_url:
            info_dict = f_parse(tree, current_url, info_dict)
        elif '/hy/' in current_url:
            info_dict = hy_parse(tree, current_url, info_dict)
        else:
            info_dict = hy_parse(tree, current_url, info_dict)
    else:
        info_dict={}
    return info_dict


def hy_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="article-bread fL"]/a/text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//h1[@class="main-title"]/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="date"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artibody"]//p/text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artibody"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@id="keywords"]//a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//a[@class="source ent-source"]/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict


def ct_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="fL article-bread"]/a/text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="page-head"]/h1/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time-source"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]//p/text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-keywords"]//a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time-source"]/a/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict


def f_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="fL article-bread"]/a/text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="page-head"]/h1/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time-source"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]//p/text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-keywords"]//a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time-source"]/a/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict


def ihmuuiyv_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = ''.join(tree.xpath('//div[@class="article-bread fL"]/a//text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//h1[@class="main-title"]/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="date"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artibody"]//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artibody"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="keywords"]//a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//a[@class="source ent-source"]/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict

def hy_ifxeuwws_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = ''.join(tree.xpath('//div[@class="article-bread fL"]/a//text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//h1[@class="main-title"]/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="date"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artibody"]//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="artibody"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="keywords"]//a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//a[@class="source ent-source"]/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict


def hy_ihmutuec_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="mainNav"]/a[position()<4]/text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="art_title"]/h1/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time"]/text()')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="art_content"]//p//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="art_content"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="tags_ul clearfix"]/a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="prot"]/span[2]/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict


def ct_ifyhwefp_parse(tree, current_url, info_dict):
    info_dict['URL'] = current_url
    info_dict['FLLJ'] = '/'.join(tree.xpath('//div[@class="fL article-bread"]/a/text()'))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="page-head"]/h1/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time-source"]/text()[1]')))
    info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S') if publish_time else datetime.now()
    info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]/p//text()')))
    info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@id="articleContent"]//img/@src')))
    info_dict['KEY_WORDS'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-keywords"]/a/text()')))
    info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//span[@class="time-source"]/a/text()')))
    info_dict['READ_NUM'] = ''
    info_dict['COMMENTS_NUM'] = get_comments_num(current_url)
    info_dict['CRAWLER_TIME'] = datetime.now()
    return info_dict


def get_comments_num(current_url):
    base_url = 'http://comment.sina.com.cn/page/info'
    current_timestamp = int(time.time()*1000)
    params = {
        'version':'1',
        'format':'json',
        'channel':'qc',
        'newsid':'comos-%s' % current_url.split('-')[-1][1:-6],
        'group':'undefined',
        'compress':'0',
        'ie':'utf-8',
        'oe':'utf-8',
        'page':'1',
        'page_size':'3',
        't_size':'3',
        'h_size':'3',
        'thread':'1',
        'callback':'jsonp_%d' % current_timestamp,
        '_':'%d' % current_timestamp
    }
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'
    }
    try:
        resp = requests.get(base_url, params=params, headers=header)
        html = resp.text
        js = ''.join(re.findall(r'jsonp_\d+?\((.*?)\)', html))
        jl = json.loads(js)
        # print(jl)
    except:
        return '0'
    else:
        comments_num = jl.get('result', {}).get('count', {}).get('total', '')
        return str(comments_num)
    