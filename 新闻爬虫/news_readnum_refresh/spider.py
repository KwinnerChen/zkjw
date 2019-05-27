#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


# 继承自BaseSpider，必须实现response_parse方法，
# 定义类变量name
# 定义初始链接start_urls（列表），或者重新定义start_requests方法
# 对于回掉函数无需返回任务时可以直接返回None
# 返回任务对象在Commons.common.Task


from Commons.common import BaseSpider
from Commons.storage import Oracle
from Commons.common import Task, Erro
from Commons.selector import Selector
import re
import demjson


class Spider(BaseSpider):
    
    name = 'news_refresh'
    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }
    oracle = Oracle('beiqi_vmda', 'tiger', '10.30.53.12:1521/orcl')

    def start_request(self):
        data = self.oracle.getall('CRAW_NEWS_ZHONGYAO', 'URL', WHERE='PUBLISH_TIME>SYSDATE-3')
        urls = (i[0] for i in data)
        for url in urls:
            if 'sohu' in url:
                yield Task(url=url, method='get', headers=self.header, callback=self.get_sohu_readnum)
            elif 'qctt' in url:
                yield Task(url=url, method='get', headers=self.header, callback=self.get_qctt_readnum)
            elif 'autohome' in url:
                objid = url.split('/')[-1].split('.')[0]
                url_ = 'https://www.autohome.com.cn/ashx/AjaxIndexArticleCount.ashx'
                params = {
                    'callback': 'callback',
                    'objids': objid,
                    'dateType':'jsonp'
                    }
                yield Task(url=url_, method='get', headers=self.header, params=params, callback=self.get_autohome_readnum, temp=url)
            elif 'bitauto' in url:
                url_ = 'http://cmsapi.bitauto.com/news3/v1/news/traffic'
                news_id = ''.join(i.strip() for i in re.findall(r'.*/\d{3}(\d+)+\.html', url))
                params = {
                    'callback': 'pvinitcallback20',
                    'ids': news_id
                    }
                yield Task(url=url_, method='get', headers=self.header, params=params, callback=self.get_yiche_readnum, temp=url)

    def get_sohu_readnum(self, response):
        if isinstance(response, Erro):
            return Task(url=response.url, method=response.method, callback=response.callback)
        selector = Selector(response, encoding='utf-8')
        read_num = ''.join(selector.xpath('//div[@class="l read-num"]/text()'))
        read_num_n = ''.join(selector.findall(r'阅读[(（]([\d\w\.]+)[)）]', read_num)) if read_num else read_num
        read_num_n = read_num_n if '万' not in read_num_n else str(int(float(read_num_n.replace('万', ''))*10000))
        self.oracle.exeSQL("UPDATE CRAW_NEWS_ZHONGYAO SET READ_NUM='%s' WHERE URL='%s'" % (read_num_n, selector.url))
        print(selector.url,'更新为', read_num_n)

    def get_qctt_readnum(self, response):
        if isinstance(response, Erro):
            return Task(url=response.url, method=response.method, callback=response.callback)
        selector = Selector(response)
        part2 = list(filter(None, (x.strip() for x in selector.xpath('//div[@class="content_detail_left"]/div[@class="part2"]//text()') if x)))
        read_num = part2[-1]
        # print(selector.url, read_num)
        self.oracle.exeSQL("UPDATE CRAW_NEWS_ZHONGYAO SET READ_NUM='%s' WHERE URL='%s'" % (read_num, selector.url))
        print(selector.url,'更新为', read_num)

    def get_yiche_readnum(self, response, temp):
        if isinstance(response, Erro):
            return Task(url=response.url, method=response.method, callback=response.callback, temp=response.temp)
        selector = Selector(response)
        js = ''.join(selector.findall(r'"\d+":({.*?}).*'))
        jl = demjson.decode(js)
        if jl:
            read_num = jl.get('pv', '0')
        else:
            read_num = '0'
        # print(temp, read_num)
        self.oracle.exeSQL("UPDATE CRAW_NEWS_ZHONGYAO SET READ_NUM='%s' WHERE URL='%s'" % (read_num, temp))
        print(selector.url,'更新为', read_num)

    def get_autohome_readnum(self, response, temp):
        if isinstance(response, Erro):
            return Task(url=response.url, method=response.method, callback=response.callback, temp=response.temp)
        selector = Selector(response)
        js = ''.join(selector.findall(r'callback\((.*?)\)'))
        jl = demjson.decode(js)
        nlist = jl['list']
        if nlist:
            read_num = nlist[0].get('ArticleCount')
            # print(temp, read_num)
            self.oracle.exeSQL("UPDATE CRAW_NEWS_ZHONGYAO SET READ_NUM='%s' WHERE URL='%s'" % (read_num, temp))
            print(selector.url,'更新为', read_num)
            
