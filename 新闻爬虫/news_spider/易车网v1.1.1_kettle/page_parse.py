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
        if 'api' not in current_url and 'news' not in current_url:
            caid = re.search(r'categoryIds:"([\d,]+)"', html).group(1)
            next_url = 'http://api.admin.bitauto.com/news3/v1/piece/GetNews?callback=getPieceNewsList&categoryIds=%s&pageIndex=2&pageSize=20&imageSize=&copyRight=0' % caid
            tree = etree.HTML(html)
            urls = map(lambda x: urljoin('http://www.autoreport.cn/', x), tree.xpath('//div[@class="inner-box"]/div[@class="details"]/h2/a/@href'))
        elif 'news' in current_url and html:
            tree = etree.HTML(html)
            urls = tree.xpath('//div[@class="article-card horizon"]//h2/a/@href')
            next_url_part = ''.join(tree.xpath('//div[@class="pagination"]//a[@class="next_on"]/@href'))
            next_url = urljoin(current_url, next_url_part) if next_url_part else None
        else:
            js = re.search(r'News":(\[.*\])', html)
            js = js.group(1) if js else '[]'
            jl = demjson.decode(js)
            urls = map(lambda x: urljoin('http://www.autoreport.cn/', x.get('Url')), jl)
            current_page_num = re.search(r'pageIndex=(\d+)', current_url)
            current_page_num = current_page_num.group(1) if current_page_num else None
            next_url = re.sub(r'pageIndex=\d+', 'pageIndex=%s' % str(int(current_page_num )+ 1), current_url) if current_page_num else None
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
        if 'autoreport' in current_url:
            info_dict['URL'] = current_url
            info_dict['FLLJ'] = '/'.join(map(lambda x: x.strip(), tree.xpath('//div[@class="crumbs-txt"]//a/text()')))
            info_dict['TITLE'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="cont-box"]//h1/text()')))
            publish_time1 = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-information"]/text()')))
            publish_time2 = ''.join(i.strip() for i in tree.xpath('//div[@class="t-box"]/span[1]/text()'))
            publish_time = publish_time1 or publish_time2
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else None
            info_dict['DATA_SOURCE'] = '易车'
            info_dict['CONTENT'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-content"]//p//text()')))
            info_dict['IMAGE_URL'] = ', '.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-content"]//img/@src')))
            info_dict['COMMENTS_NUM'] = get_comments_num(response)
            info_dict['KEY_WORDS'] = get_key_words(response)
            info_dict['READ_NUM'] = ''
            info_dict['CRAWLER_TIME'] = datetime.now()
        else:
            info_dict['DATA_SOURCE'] = '易车'
            info_dict['URL'] = current_url
            info_dict['FLLJ'] = '/'.join(x.strip() for x in tree.xpath('//div[@class="crumbs-txt"]//a/text()'))
            info_dict['TITLE'] = ''.join(x.strip() for x in tree.xpath('//div[@class="cont-box"]//h1/text()'))
            publish_time1 = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="article-information"]/text()')))
            publish_time2 = ''.join(i.strip() for i in tree.xpath('//div[@class="t-box"]/span[1]/text()'))
            publish_time = publish_time1 or publish_time2
            info_dict['PUBLISH_TIME'] = datetime.strptime(publish_time, '%Y-%m-%d %H:%M') if publish_time else None
            info_dict['CONTENT'] = ''.join(i.strip() for i in tree.xpath('//div[@class="article-content motu_cont"]//p//text()'))
            info_dict['IMAGE_URL'] = ', '.join(i.strip() for i in tree.xpath('//div[@class="article-content motu_cont"]//img/@src'))
            info_dict['KEY_WORDS'] = '/'.join(i.strip() for i in tree.xpath('//div[@class="lef-box"]/a/text()'))
            rc_num = get_read_comments_num(response)
            info_dict['READ_NUM'] = rc_num[0]
            info_dict['COMMENTS_NUM'] = rc_num[1]
            info_dict['CRAWLER_TIME'] = datetime.now()
    else: 
        info_dict={}
    return info_dict


def get_comments_num(response):
    current_url = response.url
    cur_id = current_url.split('/')[-1].split('.')[0][3:]
    resp = page_downloader('http://www.autoreport.cn/comment/NewsCommentHandlerN.aspx?type=0&id=%s' % cur_id)
    html = resp.text
    num = ''.join(re.findall(r'<span>已有<em>(\d+)人</em>参与评论', html))
    return num
    
    
def get_read_comments_num(response):
    base_url = 'http://cmsapi.bitauto.com/news3/v1/news/traffic'
    current_url = response.url
    news_id = ''.join(i.strip() for i in re.findall(r'.*/\d{3}(\d+)+\.html', current_url))
    params = {
        'callback': 'pvinitcallback20',
        'ids': news_id
        }
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
        }
    resp = page_downloader(base_url, params=params)
    html = resp.text
    js = ''.join(re.findall(r'"\d+":({.*?}).*', html))
    jl = demjson.decode(js)
    if jl:
        read_num = jl.get('pv', '0')
        comments_num = jl.get('comments', '0')
    else:
        read_num = '0'
        comments_num = '0'
    return read_num, comments_num


def get_key_words(response):
    current_url = response.url
    cur_id = current_url.split('/')[-1].split('.')[0][3:]
    resp = page_downloader('http://api.admin.bitauto.com/news3/v1/news/tags?callback=getTagData&ids=%s' % cur_id)
    html = resp.text
    key_words = '/'.join(re.findall(r'"name":"(\w+?)",', html))
    return key_words