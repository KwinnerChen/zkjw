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
        rjson = re.search(r'jQuery[\d_]+\((.*)\)', html).group(1)
        jl = demjson.decode(rjson)
        if jl:
            urls = map(lambda x: x.get('url', ''), jl)
            last_id = jl[-1].get('id', '')
            # http://api.tool.chexun.com/news/getNewsInfo.do?num=10&callback=jQuery111204700629956243153_1540721149071&type=0&seriesId=0&newsId=107739475&ccfFlag=1
            if 'newsId' in current_url:
                next_url = re.sub(r'newsId=\d+', 'newsId=%s'%last_id, current_url)
            else:
                next_url = current_url+'&newsId=%s' % last_id
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
        html = response.text
        tree = etree.HTML(html)
        current_url = response.url
        fllj_1 = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="newsbraedline clearfix"]//a/text()')))
        fllj_2 = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-bread"]//a/text()')))
        if fllj_1:
            info_dict['FLLJ'] = fllj_1
            parse_1(html, tree, current_url, info_dict)
        elif fllj_2:
            info_dict['FLLJ'] = fllj_2
            parse_2(html, tree, current_url, info_dict)
        info_dict['KEY_WORDS'] = ''
        info_dict['CRAWLER_TIME'] = datetime.now()
        info_dict['READ_NUM'] = ''
        info_dict['COMMENTS_NUM'] = ''
    else:
        info_dict={}
    return info_dict


def json_parse_1(html, current_url, info_dict):
    json_url = current_url.split('.html')[0] + '.json'
    resp = page_downloader(json_url)
    if resp:
        html = resp.text
        js = re.search(r'cxnews\((.*)\)', html).group(1)
        try:
            jl = demjson.decode(js)
        except Exception as e:
            print('json解析出错：%s'%e)
            tree = etree.HTML(html)
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-editbox"]//p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-editbox"]//img/@src')))
        else:
            gether_html = ''.join(map(lambda x: x.get('content', ''), jl.get('news', {})))
            tree = etree.HTML(gether_html)
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//img/@src')))
    else:
        tree = etree.HTML(html)
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-editbox"]//p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-editbox"]//img/@src')))


def parse_1(html, tree, current_url, info_dict):
    info_dict['URL'] = current_url
    # info_dict['fllj'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="newsbraedline clearfix"]//a/text()')))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]/h1/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//span[@class="time"]/text()')))
    publish_time = datetime.strptime(publish_time, '%Y年%m月%d日 %H:%M') if publish_time else datetime.now()
    info_dict['PUBLISH_TIME'] = publish_time
    # info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-author"]/em/text()')))
    info_dict['DATA_SOURCE'] = '车讯网'
    if '全文浏览' in html:
        json_parse_1(html, current_url, info_dict)
    else:
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-editbox"]//p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-box"]//div[@class="news-editbox"]//img/@src')))


def parse_2(html, tree, current_url, info_dict):
    info_dict['URL'] = current_url
    # info_dict['fllj'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-bread"]//a/text()')))
    info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]/h1/text()')))
    publish_time = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//span[@class="time"]/text()')))
    publish_time = datetime.strptime(publish_time, '%Y年%m月%d日 %H:%M') if publish_time else datetime.now()
    info_dict['PUBLISH_TIME'] = publish_time
    # info_dict['DATA_SOURCE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-author"]/em/a/text()')))
    info_dict['DATA_SOURCE'] = '车讯网'
    if '全文浏览' in html:
        json_parse_2(html, current_url, info_dict)
    else:
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-editbox mt20"]//p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-editbox mt20"]//img/@src')))


def json_parse_2(html, current_url, info_dict):
    json_url = current_url.split('.html')[0] + '.json'
    resp = page_downloader(json_url)
    if resp:
        html = resp.text
        js = re.search(r'cxnews\((.*)\)', html).group(1)
        try:
            jl = demjson.decode(js)
        except Exception as e:
            print('json解析出错：%s'%e)
            tree = etree.HTML(html)
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-editbox mt20"]//p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-editbox mt20"]//img/@src')))
        else:
            gether_html = ''.join(map(lambda x: x.get('content', ''), jl.get('news', {})))
            tree = etree.HTML(gether_html)
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//img/@src')))
    else:
        tree = etree.HTML(html)
        info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-editbox mt20"]//p//text()')))
        info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="news-cnt"]//div[@class="news-editbox mt20"]//img/@src')))