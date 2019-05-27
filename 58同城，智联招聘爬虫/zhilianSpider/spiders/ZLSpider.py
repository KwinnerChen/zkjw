#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/9/11 16:14
# @Author   : zequan.shao
# @File     : ZLSpider.py
# @Software : PyCharm

import requests
from queue import Queue
from scrapy import Selector

import json
import time
import random
import threading

import os
import sys

# reload(sys)
# sys.setdefaultencoding('utf-8')
# sys.path.append(r'F:\zkjw\code\zhilianNoScrapy\zhilianSpider')
# sys.path.append(r'F:\zkjw\code\zhilianNoScrapy\zhilianSpider\SqlOptions\MyMysqlOption')
# sys.path.append(r'F:\zkjw\code\zhilianNoScrapy')

from SqlOptions.MysqlOption import MysqlOption


class ZLSpider:

    metux = threading.Lock()

    def __init__(self):

        self.queue = Queue(60) # 存放详情页面url

        self.content_queue = Queue(200)

        self.header_api = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
            'Host': 'fe-api.zhaopin.com',
        }

        self.header_page = {

            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',

        }

        self.mysql = MysqlOption()

    # 发送请求,并返回一个response的迭代器
    def request_from_url(self):

        while True:

            item = self.queue.get()

            if not item:
                continue

            try:
                time.sleep(random.uniform(1.5, 4))

                response = requests.get(item['detail_url'], self.header_page)

                yield response, item

            except Exception as e:

                print (e)
                print (item['detail_url'])

                if not os.path.exists('./wrongurl'):

                    os.makedirs('./wrongurl')

                with open('./wrongurl/pageUrl.txt', 'a+') as fp:

                    fp.write(item['detail_url']+'\n')
                # raise ValueError('请求失败，请查看原因！')
                continue

    # 请求并解析详情页面
    def parse_detail(self, response, item):

        if response.status_code == 200:

            print(u'----------------------详情页面加载哟！------------------------')

            res = Selector(text=response.text)

            gshy = res.xpath('/html/body/div[@class="terminalpage clearfix"]/div[2]/div[1]/ul/li')
            xl_zprs = res.xpath('/html/body/div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/ul/li')
            zwms = res.xpath('/html/body/div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/div[@class="terminalpage-main clearfix"]/div/div[1]//text()')
            company = res.xpath('/html/body/div[@class="terminalpage clearfix"]/div[@class="terminalpage-left"]/div[@class="terminalpage-main clearfix"]/div/div[2]//text()')

            if xl_zprs:

                for li in xl_zprs:

                    lb_span = li.xpath('span/text()').extract()

                    if lb_span:

                        lbs = ''

                        for lb in lb_span:
                            lbs += lb

                        lbs = lbs.strip()

                        if lbs == '招聘人数：':
                            rs = li.xpath('strong/text()').extract()

                            for r in rs:
                                item['job_rs'] += r.replace('\t', '').replace('\r', '').strip()

                        elif lbs == '最低学历：':
                            xl = li.xpath('strong/text()').extract()

                            for x in xl:
                                item['job_xl'] += x.replace('\t', '').replace('\r', '').strip()

            else:
                print(xl_zprs)

            if gshy:

                for li in gshy:

                    lb_span = li.xpath('span/text()').extract()

                    if lb_span:

                        lbs = ''

                        for lb in lb_span:
                            lbs += lb

                        lbs = lbs.strip()

                        if lbs == '公司地址：':
                            dz = li.xpath('strong/text()').extract()

                            for d in dz:
                                item['job_gsdz'] += d.replace('\t', '').replace('\r', '').strip()

                        elif lbs == '公司行业：':
                            hy = li.xpath('strong//text()').extract()

                            for h in hy:
                                item['job_gshy'] += h.replace('\t', '').replace('\r', '').strip()

            if zwms:

                for ms in zwms.extract():
                    item['job_zwms'] += ms.replace('\t', '').replace('\r', '').strip()

            if company:

                for com in company.extract():
                    item['job_company'] += com.replace('\t', '').replace('\r', '').strip()

            self.content_queue.put(item)

            print (u'目前详情页面队列长度：', self.content_queue.qsize())

        else:

            print (u'访问详情页面失败，错误代码为：', response.status_code)
            print (u'此时的链接为：', response.url)

            if not os.path.exists('./wrongurl'):
                os.makedirs('./wrongurl')

            with open('./wrongurl/pageUrl.txt', 'a+') as fp:

                fp.write(response.url + '\n')

    # 调度详情页面请求以及解析
    def engin_detial(self):

        print(u'第二个线程正在运行。。。')

        for resp, item in self.request_from_url():
            self.parse_detail(resp, item)

    # 获取api数据
    def get_data_from_api(self, keyword):

        print(u'第一个线程正在运行。。。')

        if not keyword:
            print (u'搜索的职位为：', keyword)
            return

        base_url = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=639&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1'

        con_dict = {
            "pageSize": "60",
            "jl": "639",
            "kw": keyword,
            "kt": "3"
        }

        else_con = '&kw=' + str(keyword) + '&kt=3&lastUrlQuery=' + str(con_dict)

        print(base_url+else_con)

        data_count = self.request_api(base_url+else_con)

        if data_count:

            try:
                page_size = int(con_dict["pageSize"])
                page_num = int(int(data_count) / page_size + 1) if int(data_count) % page_size == 0 else int(int(data_count) / page_size + 2)

                start = 3540
                for i in range(60, page_num):
                    print('爬取', base_url+else_con, ' 第 ', i, ' 页...')
                    con_dict['p'] = str(i)

                    base_url1 = 'https://fe-api.zhaopin.com/c/i/sou?start=' + str(start) + '&pageSize=60&cityId=639&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1'
                    else_con = '&kw=' + str(keyword) + '&kt=3&lastUrlQuery=' + str(con_dict)

                    self.request_api(base_url1 + else_con)
                    start += 60

            except Exception as e:

                print (e)
                print(u'请求下一页的API坏掉了！！')
                print(page_num, page_size, data_count)
                input()

    # 请求api,获取更新时间以及详情页面url
    def request_api(self, url):

        print(u'----------------------请求API中哟！------------------------')

        try:
            time.sleep(random.uniform(1.5, 4))

            res = requests.get(url, headers=self.header_api)
            # res.apparent_encoding

        except Exception as e:

            print(e)
            print(url)

            if not os.path.exists('./wrongurl'):
                os.makedirs('./wrongurl')

            with open('./wrongurl/apiUrl.txt', 'a+', encoding='utf-8') as fp:

                fp.write(url + '\n')
            return
        # print(res.status_code)
        # print(res.content)
        content_dicts = json.loads(res.content)

        for content_dict in content_dicts.get('data', {}).get('results', []):

            item = self.items()

            page_url = content_dict.get('positionURL', '')
            item['detail_url'] = page_url
            item['job_id'] = page_url.split('/')[-1].split('.')[0]
            item['job_bt'] = content_dict.get('jobName', '')
            item['job_yx'] = content_dict.get('salary', '')
            item['job_gznx'] = content_dict.get('workingExp', {}).get('name', '')
            item['job_zpdd'] = content_dict.get('city', {}).get('display', '')
            item['job_xz'] = content_dict.get('emplType', '')
            item['job_gsmc'] = content_dict.get('company', {}).get('name', '')
            item['job_gsgm'] = content_dict.get('company', {}).get('size', {}).get('name', '')
            item['job_gsxz'] = content_dict.get('company', {}).get('type', {}).get('name', '')
            item['job_gszy'] = content_dict.get('company', {}).get('url', '')
            item['job_fbsj'] = content_dict.get('updateDate', '')
            item['data_source'] = 'zl'
            item['crawer_time'] = time.strftime('%Y-%m-%d %H:%M:%S')

            industry_span = content_dict.get('jobType', {}).get('display', '').split(',')
            if len(industry_span) < 2:
                item['job_zwlb'] = industry_span[0]

            else:
                item['job_zwlb'] = industry_span[0]
                item['hybq'] = industry_span[1]

            try:
                cun = 1
                for li in content_dict.get('welfare', []):
                    item['job_gsfl{}'.format(str(cun))] = li
                    cun += 1

                    # key = 'job_gsfl' + str(cun)
                    #
                    # item[key] = li
                    #
                    # cun += 1

            except Exception as e:
                print(e)

            self.queue.put(item)

            print(u'目前请求队列长度：', self.queue.qsize())

        return content_dicts.get('data', {}).get('numFound', '')

    # 通用字典
    def items(self):

        items = {
            'job_id': '',
            'job_bt': '',
            'job_yx': '',
            'job_gznx': '',
            'job_rs': '',
            'job_zpdd': '',
            'job_xz': '',
            'job_xl': '',
            'job_zwlb': '',
            'job_zwms': '',
            'job_company': '',
            'job_gsmc': '',
            'job_gsgm': '',
            'job_gsxz': '',
            'job_gshy': '',
            'job_gsdz': '',
            'job_gszy': '',
            'hybq': '',
            'job_gsfl1': '',
            'job_gsfl2': '',
            'job_gsfl3': '',
            'job_gsfl4': '',
            'job_gsfl5': '',
            'job_gsfl6': '',
            'job_gsfl7': '',
            'job_gsfl8': '',
            'job_fbsj': '',
            'data_source': '',
            'crawer_time': '',
            'detail_url': '',
        }

        return items

    # 数据写入
    def data_storage(self):

        print(u'第三个线程正在运行。。。')

        while True:

            item = self.content_queue.get()
            self.mysql.insert_option(item)

