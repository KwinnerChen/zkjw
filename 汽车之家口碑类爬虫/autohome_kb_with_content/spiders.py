#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


# 继承自BaseSpider，必须实现response_parse方法，
# 定义类变量name
# 定义初始链接start_urls（列表），或者重新定义start_requests方法


from Commons.common import BaseSpider
from Commons.common import Task
from Commons.common import TimeVerify
from Commons.common import Erro
from Commons.selector import Selector
from Commons.IPPool import IPPoolManager
from datetime import datetime
from urllib.parse import urljoin, unquote
from fontparse_kb import FontParse
import cx_Oracle
import config
import os
import re
import requests
#import xlrd


# ORACLE口碑自增序列名KB_ID_SEQ
# 口碑印象自增序列KBIMPRESSION_ID_SEQ
# 车型数据表对应表自增序列CARID_ID_SEQ
# 插入时：INSERT INTO CRAW_KB(ID, USERNAME, ...) VALUES (KB_ID_SEQ.NEXTVAL, '用户', ...)
# 要17年之后的数据
# 使用了oracle自增序列，所以要改写一下存储模块
# KB_REAL_SEQ, IMPRESSION_REAL_SEQ
# 口碑移动网址https://k.m.autohome.com.cn/detail/view_01csvzrtq168s36e9g6rv00000.html


os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class Spider(BaseSpider):
    cookie = {'sessionlogin': 'ab6c6ed1a0d048049c2bd6496d88a273058bb878'}

    cookie_r = {
        'autosso': 'eddc0e0a08694e279f9063ec64d40691058bb878',
        'autouserid': '93042808'
    }

    header = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
    }
    
    name = 'increment_koubei' 

    # manager = IPPoolManager()
    manager = IPPoolManager()
    ippool = manager.get_ippool()
    # ippool = get_ippool()

    timeverifier = TimeVerify(increment=1)  # 需要跨实例使用

    def start_request(self):
        base_url = 'https://k.autohome.com.cn/{TYPEID}/ge0/0-0-2/'
        con = cx_Oracle.connect('bq_data', 'tiger', '39.107.57.229:1521/orcl.lan')
        cur = con.cursor()
        cur.execute("select CARTYPE, CARID from CRAW_KB_CARID2CARTYPE where CARTYPE in (select CNAME from BBS_TABLENAME)")
        carlist = cur.fetchall()
        cur.close()
        con.close()
        for i in carlist:
            #print(i)
            url = base_url.format(TYPEID=i[1])
            #url = base_url.format(TYPEID=235)
            cartype = i[0]
            #cartype = '奔驰CLK级'
            yield Task(url=url, method='get', callback=self.content_parse, temp=cartype, headers=self.header, proxies=self.ippool.get())

    def content_parse(self, response, temp):
        task_list = []
        if isinstance(response, Erro):
            return Task(url=response.url, method='get', callback=self.content_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        if 'safety' in response.url:
            url = response.url.split('=')[-1]
            url = urljoin('https://', unquote(url))
            print('%s 遇到验证，重新下载！'%url)
            return Task(url=url, method='get', callback=self.content_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        selector = Selector(response)
        root_nodes = selector.xpath('//div[@class="mouthcon"]') # 汽车信息
        time_node = selector.xpath('//div[@class="title-name name-width-01"]//b/a/text()') # 获取时间列表
        ltime = max(time_node) # 靠前时间
        # page_node = selector.xpath('//dic[@class="page-cont"]')
        if len(root_nodes)<15 and ltime<='2016-08-25' and temp not in ' '.join(i.strip() for i in root_nodes[0].xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "购买车型")]/dd//text()')):
            print('%s 获取到迷惑页面，重新下载！'%response.url)
            return Task(url=response.url, method='get', callback=self.content_parse, temp=temp, headers=self.header, proxies=self.ippool.get())
        if self.timeverifier.timeverify(temp, ltime):
        # if ltime >= '2015-01-01':
            next_page = ''.join(i.strip() for i in selector.xpath('//div[@class="page"]/a[@class="page-item-next"]/@href'))
            next_page = urljoin(response.url, next_page) if next_page else ''
            task_list.append(Task(url=next_page, method='get', callback=self.content_parse, temp=temp, headers=self.header, proxies=self.ippool.get()))
        if not self.timeverifier.timeverify(temp, ltime):
        # if '2017-01-01' <= ltime or ltime < '2015-01-01':
            print('日期超限！', response.url)
            self.timeverifier.log_logpkl()
            return

        for node in root_nodes:
            item = {}
            ctime = ''.join(i.strip() for i in node.xpath('.//div[@class="title-name name-width-01"]//b/a/text()')[-1])
            if not self.timeverifier.timeverify(temp, ctime):
            # if '2017-01-01' <= ltime or ltime < '2015-01-01':
                continue
            item['PUBLISHTIME'] = datetime.strptime(ctime, '%Y-%m-%d')
            userid = ''.join(i.strip() for i in node.xpath('.//div[@class="name-text"]/p/a/@href')).split('/')[-1]
            item['USERID'] = userid or ''
            item['CARVERSION'] = ' '.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "购买车型")]/dd//text()'))
            timebying = ''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "购买时间")]/dd//text()'))
            item['TIMEBYING'] = datetime.strptime(timebying, '%Y年%m月')
            item['PLACEBYING'] = ' '.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "购买地点")]/dd//text()'))
            item['PURPOSEBYING'] = ' '.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "购车目的")]/dd//text()'))
            item['KJ'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "空间")]/dd//text()')))
            item['DL'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "动力")]/dd//text()')))
            item['CK'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "操控")]/dd//text()')))
            yh = node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "油耗")]/dd//text()')
            hd = node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "耗电量")]/dd//text()')
            item['YH'] = int(''.join(i.strip() for i in yh)[-1]) if yh and re.match(r'\d+', ''.join(i.strip() for i in yh)[-1]) else None
            item['HD'] = int(''.join(i.strip() for i in hd)[-1]) if hd and re.match(r'\d+', ''.join(i.strip() for i in hd)[-1]) else None
            item['SS'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "舒适性")]/dd//text()')))
            item['WG'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "外观")]/dd//text()')))
            item['NS'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "内饰")]/dd//text()')))
            item['XJB'] = int(''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "性价比")]/dd//text()')))
            item['CARTYPE'] = temp
            item['CRAWLER_TIME'] = datetime.now()
            price = ''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "裸车购买价")]/dd//text()')).replace('万元', '')
            item['PRICE'] = price
            youhao = ''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "油耗")]/dd/p/text()'))
            haodianliang = ''.join(i.strip() for i in node.xpath('.//div[@class="choose-con mt-10"]//dl[contains(dt, "耗电量")]/dd/p/text()'))
            item['HAODIAN'] = '%.1f' % float(haodianliang) if haodianliang.count('.')==1 else None
            item['YOUHAO'] = '%.1f' % float(youhao) if youhao.count('.')==1 else None
            kbcontent_url = ''.join(node.xpath('.//a[contains(text(), "查看全部内容")]/@href'))
            kbcontent_id = ''.join(selector.findall(r'view_(.*?)\.html', kbcontent_url))
            task_list.append(Task(url='https://k.m.autohome.com.cn/detail/view_%s.html'%kbcontent_id, method='get', callback=self.get_content, temp=item, proxies=self.ippool.get(), headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}))
            # task_list.append(Task(url='https://i.autohome.com.cn/{userid}/info'.format(userid=userid), method='get', callback=self.user_info_parse, temp=item, headers=self.header, cookies=self.cookie))      
        # 获取当前页最新时间，小于规定时间则不翻页
        # print(task_list)
        return task_list

    def get_content(self, response, temp):
        if isinstance(response, Erro):
            print('返回错误对象，任务返回到任务列队！')
            return Task(url=response.url, method='get', callback=self.get_content, temp=temp, headers=self.header, proxies=self.ippool.get())
        if 'safety' in response.url:
            url = response.url.split('=')[-1]
            url = urljoin('https://', unquote(url))
            print('%s 遇到验证，刷新cookie重新下载！'%url)
            self.__cookie_refresh()
            return Task(url=url, method='get', callback=self.get_content, temp=temp, headers=self.header, proxies=self.ippool.get())
        selector = Selector(response)
        font = FontParse(response)
        item = temp
        root_node = selector.xpath('//div[@class="matter"]')
        root_node = root_node[-1] if root_node else []
        satisfied = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "最满意")]//span/text()'))
        unsatisfied = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "最不满意")]//span/text()'))
        why = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "为什么选择这款车")]//span/text()'))
        space = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "空间")]//span/text()'))
        power = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "动力")]//span/text()'))
        control = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "操控")]//span/text()'))
        comfort = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "舒适性")]//span/text()'))
        appearance = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "外观")]//span/text()'))
        trim = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "内饰")]//span/text()'))
        costperf = ''.join(i.strip() for i in root_node.xpath('./div[contains(h4, "性价比")]//span/text()'))
        if not any((satisfied, unsatisfied, why, space, power, control, comfort, appearance, trim, costperf)):
            print('%s相应页面未解析出内容，返回任务列队重新下载' % response.url)
            return Task(url=response.url, method='get', callback=self.get_content, temp=temp, headers=self.header, proxies=self.ippool.get())
        item['SATISFIED'] = font.string2font(satisfied)
        item['UNSATISFIED'] = font.string2font(unsatisfied)
        item['WHY'] = font.string2font(why)
        item['SPACE'] = font.string2font(space)
        item['POWER'] = font.string2font(power)
        item['CONTROL'] = font.string2font(control)
        item['COMFORT'] = font.string2font(comfort)
        item['APPEARANCE'] = font.string2font(appearance)
        item['TRIM'] = font.string2font(trim)
        item['COSTPERF'] = font.string2font(costperf)
        userid = item['USERID']
        del font
        return Task(url='https://i.autohome.com.cn/{userid}/info'.format(userid=userid), method='get', callback=self.user_info_parse, temp=item, headers=self.header, cookies=self.cookie)

    def user_info_parse(self, response, temp):
        if isinstance(response, Erro):
            return Task(url=response.url, method='get', callback=self.user_info_parse, temp=temp, headers=self.header, cookies=self.cookie)
        selector = Selector(response)
        gender = ''.join(i.strip() for i in selector.xpath('//div[@class="uData"]/p[contains(span, "性别")]/text()'))
        birthday = ''.join(i.strip() for i in selector.xpath('//div[@class="uData"]/p[contains(span, "生日")]/text()'))
        domicile = ''.join(i.strip() for i in selector.xpath('//div[@class="uData"]/p[contains(span, "所在地")]/text()'))
        yearsold = datetime.now().year - datetime.strptime(birthday, '%Y-%m-%d').year if birthday else None
        item = temp
        item['GENDER'] = gender
        item['YEARSOLD'] = yearsold
        item['DOMICILE'] = domicile.replace('\xa0', ' ')
        userid = item['USERID']
        if 'alert' in response.url:
            print('https://i.autohome.com.cn/%s/info 页面不存在，无法获取个人信息。' % userid)
            item['CARPORT'] = None
            return Task(item=[item])
        if not gender:  # 无法获取性别时刷新cookie
            self.__cookie_refresh()
            return Task(url='https://i.autohome.com.cn/%s/info'%userid, method='get', callback=self.user_info_parse, temp=temp, headers=self.header, cookies=self.cookie)
        baseurl = 'https://i.autohome.com.cn/ajax/home/OtherHomeAppsData?'
        url = baseurl + 'appname=Car&TuserId=%s' % userid
        header = {
            'Referer':'https://i.autohome.com.cn/%s' % userid,
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0'
        }
        return Task(url=url, method='get', callback=self.get_user_cars, temp=item, headers=header)

    def get_user_cars(self, response, temp):
        jl = response.json()  # 用户车库返回的是json
        carlist = jl.get('ConcernInfoList', [])
        if carlist:
            cars = ''
            for car in carlist:
                brandname = car.get('BrandName', '')
                seriername = car.get('SeriesName', '')
                specname = car.get('SpecName', '')
                cartype = ' '.join((brandname, seriername, specname)) + '/'
                cars += cartype
        else:
            cars = None
        item = temp
        item['CARPORT'] = cars
        return Task(item=[item])
        # print(item)

    def __cookie_refresh(self):
        url = 'https://sso.autohome.com.cn/Home/CookieIFrame'
        self.cookie_r.update(self.cookie)
        resp = requests.get(url, headers=self.header, cookies=self.cookie_r)
        new_cookie = resp.cookies.get_dict()
        self.cookie['sessionlogin'] = new_cookie.get('sessionlogin')


class InSpider(Spider):

    name = 'addspider'

    def start_request(self):
        url = 'https://k.autohome.com.cn/{TYPEID}/ge0/0-0-2/'
        sql1 = 'SELECT CARTYPE, CARID FROM CRAW_KB_CARID2CARTYPE'
        sql2 = 'SELECT CARTYPE FROM CAR_MIDD'
        con = cx_Oracle.connect('bq_data', 'tiger', '10.31.155.129:1521/orcl.lan')
        cur = con.cursor()
        data = cur.execute(sql1)
        all_cars_dict = dict(data.fetchall())
        data = cur.execute(sql2)
        crawed_car = set([i[0] for i in data.fetchall()])
        del data
        cur.close()
        con.close()
        book = xlrd.open_workbook('BBS_TABLENAME.xlsx')
        cursheet = book.sheet_by_name('BBS_TABLENAME')
        row_num = cursheet.nrows
        f = open('carlog.txt', 'a', encoding='utf-8')
        for n in range(int(row_num/2), row_num+1):
            if n == 0:
                continue
            cartype = cursheet.row(n)[1].value
            if cartype not in crawed_car:
                carid = all_cars_dict.get(cartype)
                if carid:
                    f.write(carid+', '+cartype)
                    # yield Task(url=url.format(TYPEID=carid), method='get', callback=self.content_parse, temp=cartype, headers=self.header, proxies=self.ippool.get())
                    print(Task(url=url.format(TYPEID=carid), method='get', callback=self.content_parse, temp=cartype, headers=self.header, proxies=self.ippool.get()))
        f.close()
