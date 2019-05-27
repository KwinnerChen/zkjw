#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/8/16 10:29
# @Author   : zequan.shao
# @File     : SkySpider.py
# @Software : PyCharm

import requests
import json
import random

import time

# from shuikeyuan02.items import items
from collections import OrderedDict
from shuikeyuan02 import settings
# from shuikeyuan02.log.get_path import get_path


class SkySpider(object):

    '''
    定义爬虫类，包含了发送请求、解析页面、爬虫名字和开始连接
    :return
    '''
    url_static = 'http://www.wanfangdata.com.cn/perio/articleList.do'  # 数据请求链接

    '''
        param 的参数说明：
        :page 请求的页数
        :pageSize 一页的大小
        :issue_num 发布文章的月份
        :publish_year 发布的年份
        :article_start 发布文章开始时间年份（限制条件）
        :article_end 发布文章结束时间年份（限制条件）
        :title_article 发布文章的标题
        :perio_id 发布文章的类别（期刊id）
    '''
    param = {

        'page': '1',
        'pageSize': '50',
        'issue_num': '',
        'publish_year': '',
        'article_start': '',
        'article_end': '',
        'title_article': '',
        'perio_id': '',

    }

    def __init__(self, name='', start_time='', end_time='', publish_year='', issue_num='', *start_urls_key):

        self.name = name # 爬虫名字
        self.start_urls_key = start_urls_key # 期刊的类别id

        self.header = settings.DEFAULT_REQUEST_HEADER

        if start_time:
            self.param['article_start'] = start_time

        if end_time:
            self.param['article_end'] = end_time
        else:
            print('Woring! No end_time,so set the end_time with the current time.')

            current_time = time.strftime('%Y', time.localtime(time.time()))

            print('Current year is %s'%current_time)

            self.param['article_end'] = current_time

        if issue_num:
            self.param['issue_num'] = issue_num

        if publish_year:
            self.param['publish_year'] = publish_year


    # 发起第一次请求,返回的是每个期刊的第一页数据
    '''
    该方法做了一步断点处理，这个需要的是手工录入的断点，参数m_key表示的是出现断点的期刊id
    pageNum出现错误的页数。
    '''
    def start_request(self, m_key='', pageNum=''):

        for key in self.start_urls_key:

            self.param['perio_id'] = key

            if m_key:#这里进行是否有断点期刊id的判断，以及断点页数的判断，如果有则按照断点的要求进行爬取，没有就从起始页面开始爬取
                if key == m_key:
                    if pageNum:
                        self.param['page'] = pageNum
                else:
                    self.param['page'] = '1'
            else:
                self.param['page'] = '1'

            print('============================================================')
            print(self.param['page'])
            print('============================================================')
            response = requests.post(self.url_static, data=self.param, headers=self.header)

            if response.status_code == 200:

                yield response

            else:

                print(response.status_code)

                print('Visitting data fieled! the wrong key is %s' % key)

                with open('./wrongKey.txt', 'a+') as fp:
                    fp.write(key + '\n')

                continue

    # 发送当前期刊下一页数据的请求
    def middle_request(self, pageNum):

        self.param['page'] = str(pageNum)

        if settings.USER_AGENT:
            ua = random.choice(settings.USER_AGENT)
            if ua:
                self.header['User-Agent'] = ua

        time.sleep(random.random()*6)
        res = requests.post(self.url_static, data=self.param, headers=self.header)

        if res.status_code == 200:
            return res
        else:
            print('Visited page failed,the pageNum is %s' % pageNum)
            return


    # 解析页面，返回当前期刊的所有内容，每次返回是一页的数据
    def parse(self, response):

        '''
        该网站返回的内容为 json 格式的内容
        :param response:
        :return:
        '''
        try:
            content_json = json.loads(response.content)
        except Exception as e:
            print('Non Serializable Error: %s'%e)
            return

        page_total = content_json['pageTotal']  # 一共多少页
        data_total = content_json['totalRow']  # 一共有多少数据
        current_page = content_json['pageNum']  # 当前第几页
        current_data = content_json['pageRow']  # 当前页面数据

        result = self.loop(current_page, page_total, *current_data)

        yield result

        # 判断总页数是否大于当前页数，如果大于的话，就访问下一页
        while True:

            if int(page_total) > int(current_page):

                current_page = int(current_page) + 1

                resp = self.middle_request(current_page)

                if resp:
                    try:
                        content_json = json.loads(resp.content)
                    except Exception as e:
                        print('Non Serializable Error: %s' % e)
                        print('Current pageNum is %s'%current_page)
                        continue

                    current_page = content_json['pageNum']  # 当前第几页
                    current_data = content_json['pageRow']  # 当前页面数据
                    if current_data:

                        result = self.loop(current_page, page_total, *current_data)

                        yield result

                    else:

                        current_page = current_page - 1

                else:
                    print('Visiting page Failed!!')
                    continue

            else:
                break

    # 循环获取数据
    def loop(self, current_page, data_total, *current_data):

        data_list = []

        publish_year = ''
        perio_id = ''

        for data in current_data:

            try:
                if data['article_id']:
                    article_id = data[u'article_id']  # 文章id
                else:
                    article_id = ''
            except:
                article_id = ''

            # 关键词
            keywords = ''
            try:
                if data['keywords']:
                    #for words in data[u'keywords']:
                        #keywords += words + '，'.decode('utf-8')
                    keywords = '，'.join(data['keywords'])
                    print(keywords)
            except:
                print('no keywords field!')

            # 关键词英文
            keywords_eng = ''
            try:
                if data['trans_keys']:
                    for word in data[u'trans_keys']:
                        keywords_eng += word + ','
            except:
                print('no trans_keys field!')

            try:
                if data[u'perio_id']:
                    perio_id = data[u'perio_id']  # 期刊id
                else:
                    perio_id = ''
            except:
                perio_id = ''

            try:
                if data[u'perio_title']:
                    perio_title = data[u'perio_title']  # 期刊名称
                else:
                    perio_title = ''
            except:
                perio_title = ''

            try:
                if data[u'perio_title_en']:
                    perio_title_eng = data[u'perio_title_en']  # 期刊名称英文
                else:
                    perio_title_eng = ''
            except:
                perio_title_eng = ''

            try:
                if data[u'summary']:
                    summary = data[u'summary']  # 摘要
                else:
                    summary = ''
            except:
                summary = ''

            try:
                if data[u'trans_abstract']:
                    summary_eng = data[u'trans_abstract']  # 摘要英文
                else:
                    summary_eng = ''
            except:
                print('no trans_abstract field!')
                summary_eng = ''

            try:
                if data[u'title']:
                    article_title = data[u'title']  # 文章标题
                else:
                    article_title = ''
            except:
                article_title = ''

            try:
                if data[u'trans_title']:
                    article_title_eng = data[u'trans_title']  # 文章标题英文
                else:
                    article_title_eng = ''
            except:
                print('no fund_info field!')
                article_title_eng = ''

            subject_class_codes = ''
            try:
                if data[u'subject_class_codes']:
                    if isinstance(data['subject_class_codes'], list):
                        for ji in data['subject_class_codes']:
                            subject_class_codes += ji + '，'.decode('utf-8')
                    else:
                        subject_class_codes = data[u'subject_class_codes']  # 文章分类号
                else:
                    subject_class_codes = ''
            except:
                subject_class_codes = ''

            try:
                if data[u'doi']:
                    doi = data[u'doi']  # 文章doi
                else:
                    doi = ''
            except:
                doi = ''

            try:
                if data[u'source_db']:
                    if isinstance(data['source_db'], list):
                        source_db = str(data[u'source_db'])  # 文章数据库位置
                    else:
                        source_db = data['source_db']
                else:
                    source_db = ''
            except:
                source_db = ''

            try:
                if data[u'share_num']:
                    share_num = data[u'share_num']  # 文章分享次数
                else:
                    share_num = ''
            except:
                share_num = ''

            try:
                if data[u'download_num']:
                    download_num = data[u'download_num']  # 文章下载次数
                else:
                    download_num = ''
            except:
                download_num = ''

            try:
                if data[u'page_range']:
                    page_range = data[u'page_range']  # 文章起始页以及结束页
                else:
                    page_range = ''
            except:
                page_range = ''

            try:
                page_range_s = page_range.split('-')[0]
                page_range_e = page_range.split('-')[1]
            except:
                page_range_s = page_range
                page_range_e = page_range

            try:
                if data[u'publish_year']:
                    publish_year = data[u'publish_year']  # 发布年份
                else:
                    publish_year = ''
            except:
                publish_year = ''

            try:
                if data[u'issue_num']:
                    issue_num = data[u'issue_num']  # 发布期或者卷
                else:
                    issue_num = ''
            except:
                issue_num = ''

            try:
                if data[u'fund_info']:
                    fund_info = data[u'fund_info']  # 文章中的基金
                else:
                    fund_info = ''
            except:
                print('no fund_info field!')
                fund_info = ''

            try:
                if data[u'language']:
                    language = data[u'language']  # 文章语言
                else:
                    language = ''
            except:
                language = ''

            try:
                if data[u'page_cnt']:
                    page_cnt = data[u'page_cnt']  # 文章页数
                else:
                    page_cnt = ''
            except:
                page_cnt = ''

            try:
                if data[u'is_oa']:
                    isoa = data[u'is_oa']  # isoa 参数
                else:
                    isoa = ''
            except:
                isoa = ''

            try:
                article_url = "http://www.wanfangdata.com.cn/search/downLoad.do?page_cnt=" + str(page_cnt) + "&language=" + language + "&resourceType=perio&source=" + source_db + "&resourceId=" + article_id + "&resourceTitle=" + article_title + "&isoa=" + str(isoa) + "&type=perio"
            except:
                print (page_cnt, language, source_db, article_id, article_title, isoa)
                print('url connection wrong!!')
                article_url = ''

            # 获取作者信息
            auth_list = ''
            auth_list_en = ''

            try:
                if data[u'authors_name']:
                    #for auth_name in data[u'authors_name']:
                     #   auth_list += auth_name + '，'.decode('utf-8')
                      #  print(auth_list)
                    if isinstance(data['authors_name'], list):
                        auth_list = '，'.join(data[u'authors_name'])
                        print(data['authors_name'])
                    elif isinstance(data['authors_name'], str):
                        auth_list=data['authors_name']
                    print(auth_list)   
            except:
                print('no authors name!')

            try:
                if data[u'trans_authors']:
                    for auth_name_en in data[u'trans_authors']:
                        auth_list_en += auth_name_en + ','
            except:
                print('no trans authors!')

            auth_unit = ''
            try:
                if data[u'authors_unit']:
                    if isinstance(data['authors_unit'], list):
                        for ij in data['authors_unit']:  # 作者单位
                            auth_unit += ij + '，'.decode('utf-8')
                    else:
                        auth_unit = data['authors_unit']
                else:
                    auth_unit = ''
            except:
                print('no auth_nuit field!')

            # 作者的详细信息，这里的数据格式是：[{},{}]
            try:
                if data['op']['perioAuthors']:
                    auth_detial = data['op']['perioAuthors']
                else:
                    auth_detial = []
            except:
                auth_detial = []

            item = OrderedDict()

            item['article_id'] = article_id
            item['keywords'] = keywords
            item['keywords_eng'] = keywords_eng
            item['perio_id'] = perio_id
            item['perio_title'] = perio_title
            item['perio_title_eng'] = perio_title_eng
            item['summary'] = summary
            item['summary_eng'] = summary_eng
            item['article_title'] = article_title
            item['article_title_eng'] = article_title_eng
            
            item['doi'] = doi
            item['source_db'] = source_db
            item['share_num'] = share_num
            item['download_num'] = download_num
            item['page_range'] = page_range
            item['publish_year'] = publish_year
            item['issue_num'] = issue_num
            item['fund_info'] = fund_info
            item['language'] = language
            item['page_cnt'] = page_cnt
            item['isoa'] = isoa
            item['article_url'] = article_url
            item['auth_list'] = auth_list
            item['auth_list_en'] = auth_list_en
            item['auth_unit'] = auth_unit
            item['page_range_s'] = page_range_s
            item['page_range_e'] = page_range_e
            item['auth_detial'] = auth_detial
            item['subject_class_codes'] = subject_class_codes

            data_list.append(item)

            print('Having read an article which title is %s'%article_title)

        try:

            log_info = 'The current year is %s, the perio is %s, the pageNum is %s, the number of data is %s'%(publish_year, perio_id, current_page, data_total)
            print (log_info)

            log_path =  'log-' + str(time.strftime('%Y-%m-%d')) + '.txt'
            print(log_path)

            with open(log_path, 'a+') as fp:
                fp.write(log_info + '\n')

        except Exception as e:
            print ('Log file write failed!')
            print(e)

        return data_list

