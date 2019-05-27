#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from selector import Selector
from Commons.common import Task, BaseSpider
from urllib.parse import urljoin
from datetime import datetime
import re
import json


class AuDiSpider(BaseSpider):  # 奥迪

    name = 'audi'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-14140.html', 
        'https://bbs.pcauto.com.cn/forum-14140.html', 
        'https://bbs.pcauto.com.cn/forum-14140.html', 
        'https://bbs.pcauto.com.cn/forum-14359.html', 
        'https://bbs.pcauto.com.cn/forum-14359.html', 
        'https://bbs.pcauto.com.cn/forum-16856.html', 
        'https://bbs.pcauto.com.cn/forum-16856.html', 
        'https://bbs.pcauto.com.cn/forum-16856.html', 
        'https://bbs.pcauto.com.cn/forum-17365.html', 
        'https://bbs.pcauto.com.cn/forum-17365.html', 
        'https://bbs.pcauto.com.cn/forum-17369.html', 
        'https://bbs.pcauto.com.cn/forum-17369.html', 
        'https://bbs.pcauto.com.cn/forum-17369.html', 
        'https://bbs.pcauto.com.cn/forum-17375.html', 
        'https://bbs.pcauto.com.cn/forum-17375.html', 
        'https://bbs.pcauto.com.cn/forum-17375.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-14034.html', 
        'https://bbs.pcauto.com.cn/forum-17367.html', 
        'https://bbs.pcauto.com.cn/forum-17321.html', 
        'https://bbs.pcauto.com.cn/forum-17321.html', 
        'https://bbs.pcauto.com.cn/forum-17329.html', 
        'https://bbs.pcauto.com.cn/forum-18746.html', 
        'https://bbs.pcauto.com.cn/forum-17323.html', 
        'https://bbs.pcauto.com.cn/forum-17323.html', 
        'https://bbs.pcauto.com.cn/forum-17324.html', 
        'https://bbs.pcauto.com.cn/forum-17299.html', 
        'https://bbs.pcauto.com.cn/forum-18245.html', 
        'https://bbs.pcauto.com.cn/forum-18235.html', 
        'https://bbs.pcauto.com.cn/forum-27105.html', 
        'https://bbs.pcauto.com.cn/forum-27105.html', 
        'https://bbs.pcauto.com.cn/forum-17363.html', 
        'https://bbs.pcauto.com.cn/forum-17319.html', 
        'https://bbs.pcauto.com.cn/forum-19016.html', 
        'https://bbs.pcauto.com.cn/forum-20866.html', 
        'https://bbs.pcauto.com.cn/forum-20280.html',
        'https://bbs.pcauto.com.cn/forum-19028.html', 
        'https://bbs.pcauto.com.cn/forum-20271.html', 
        'https://bbs.pcauto.com.cn/forum-27935.html', 
        'https://bbs.pcauto.com.cn/forum-20673.html', 
        'https://bbs.pcauto.com.cn/forum-20261.html', 
        'https://bbs.pcauto.com.cn/forum-20268.html', 
        'https://bbs.pcauto.com.cn/forum-20252.html', 
        'https://bbs.pcauto.com.cn/forum-20265.html', 
        'https://bbs.pcauto.com.cn/forum-28045.html', 
        'https://bbs.pcauto.com.cn/forum-23229.html', 
        'https://bbs.pcauto.com.cn/forum-20234.html', 
        'https://bbs.pcauto.com.cn/forum-26335.html', 
        'https://bbs.pcauto.com.cn/forum-20270.html', 
        'https://bbs.pcauto.com.cn/forum-25625.html', 
        'https://bbs.pcauto.com.cn/forum-26325.html', 
        'https://bbs.pcauto.com.cn/forum-20232.html', 
        'https://bbs.pcauto.com.cn/forum-28445.html', 
        'https://bbs.pcauto.com.cn/forum-28616.html', 
        'https://bbs.pcauto.com.cn/forum-28835.html'
    ]

    def get_bbs_info_list(self, response):
        selector = Selector(response)
        url_list = (urljoin(selector.url, url) for url in selector.xpath('//th[@thisforum="true"]//span[@class="checkbox_title"]/a/@href'))
        tids = selector.xpath('//th[@thisforum="true"]/@tid')
        views_num = self.__get_views_num(selector.url, tids)
        tasks = zip(url_list, views_num)
        next_url_part = ''.join(selector.xpath('//a[@class="next"]/@href'))
        next_page = urljoin(selector.url, next_url_part) if next_url_part else ''
        return (Task(url=''.join(str(i) for i in u[:1]), method='get', callback=self.page_parse, temp=''.join(str(i) for i in u[1:])) for u in tasks), Task(url=next_page, method='get', callback=self.get_bbs_info_list)


    def page_parse(self, response, temp):
        selector = Selector(response)
        tablename = ''.join(selector.findall(r"forumName[ ：:]+?'(.*?)'[,，]")).replace('论坛', '')
        bbs_id = ''.join(selector.search(r"topicI[Dd][ :：]+(.*?)[,，]").group(1) if selector.search(r"topicI[Dd][ :：]+(.*?)[,，]") else '')
        forumid = ''.join(selector.search(r"forumI[Dd][ :：]+(.*?)[,，]").group(1) if selector.search(r"forumI[Dd][ :：]+(.*?)[,，]") else '')
        bbs_bt = ''.join(selector.xpath('//div[@class="post_r_tit"]/h1[@class="yh"]/i[@id="subjectTitle"]/text()'))
        bbs_qa = '1' if selector.xpath('//div[@class="post_r_tit"]/a[contains(text(), "提问")]') else '0'
        bbs_jing = '1' if selector.xpath('//div[@class="pick1"]') or selector.xpath('//div[@class="pick2"]') else '0'
        bbs_ftsjs = (selector.search(r'\d{2,4}\-\d{1,2}\-\d{1,2}[ ]\d{1,2}:\d{1,2}', x).group() for x in selector.xpath('//table[starts-with(@id, "pid")]//div[@class="post_time"]/text()'))
        bbs_nrs = (''.join(y.strip() for y in x.xpath('./text()')) for x in selector.xpath('//table[starts-with(@id, "pid")]//div[@class="post_msg replyBody"]'))
        bbs_imgs = (', '.join(y.strip() for y in x.xpath('./img/@src')) for x in selector.xpath('//table[starts-with(@id, "pid")]//div[@class="post_msg replyBody"]'))
        user_yhms = selector.xpath('//table[starts-with(@id, "pid")]//a[starts-with(@class, "user-")]/text()')
        user_ftzs = selector.xpath('//table[starts-with(@id, "pid")]//div[@class="user_atten"]//li[contains(text(), "帖子")]/span/a/text()')
        user_jhs = selector.xpath('//table[starts-with(@id, "pid")]//div[@class="user_atten"]//li[contains(text(), "精华")]/span/a/text()')
        user_sfds_str = (''.join(x.xpath('.//a[@class="dblue"]/text()')) for x in selector.xpath('//table[starts-with(@id, "pid")]//div[@class="user_info"]'))
        user_sf = (''.join(x.split()[:1]) for x in user_sfds_str)
        user_ds = (''.join(x.split()[1:]) for x in user_sfds_str)
        bbs_hfs = ''.join(selector.xpath('//p[@class="overView"]/span[2]/text()'))
        bbs_djs = temp
        user_ids = [''.join(x.xpath('./@authorid')) for x in selector.xpath('//table[contains(@id, "pid")]//div[@class="user_info"]')]
        bbs_achgz = self.__get_user_car(selector.url, bbs_id, forumid, user_ids)
        # print(bbs_achgz)
        post_info = zip(user_yhms, bbs_nrs, bbs_imgs, bbs_ftsjs, user_ftzs, user_jhs, user_sf, user_ds, user_ids)
        next_url_part = ''.join(selector.xpath('//div[@id="pagerBottom"]//a[@class="next"]/@href'))
        next_page = urljoin(selector.url, next_url_part) if next_url_part else ''
        task_list = []
        for i in post_info:
            result_dict = dict.fromkeys(set(self.data_struct), '')
            temp_dict = {}
            temp_dict['BBS_ID'] = int(bbs_id)
            temp_dict['BBS_BT'] = bbs_bt
            temp_dict['BBS_QA'] = bbs_qa
            temp_dict['BBS_JING'] = bbs_jing
            temp_dict['BBS_HFS'] = bbs_hfs
            temp_dict['BBS_DJS'] = temp
            temp_dict['BBS_NR'] = i[1]
            temp_dict['BBS_SF'] = i[6]
            temp_dict['BBS_DS'] = i[7]
            temp_dict['BBS_FTSJ'] = i[3]
            temp_dict['BBS_YHID'] = i[8]
            temp_dict['BBS_TABLENAME'] = tablename
            temp_dict['BBS_IMG'] = i[2]
            temp_dict['BBS_YHM'] = i[0]
            temp_dict['BBS_ACHGZ'] = self.__parse_user_car(bbs_achgz, i[8])
            temp_dict['BBS_JHS'] = i[5]
            temp_dict['BBS_FTZS'] = i[4]
            temp_dict['CRAW_TIME'] = datetime.now()
            result_dict.update(temp_dict)
            task_list.append(result_dict)
        return Task(item=task_list), Task(url=next_page, method='get', callback=self.page_parse, temp=bbs_djs)

    def __parse_user_car(self, bbs_achgz, user_id):
        for d in bbs_achgz:
            if d.get('vipid', '') == int(user_id):
                car_type = d.get('modelname', '')
                break
        else:
            car_type = ''
        return car_type

    def __get_views_num(self, cur_url, tids):
        import requests
        header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Host':'bbs.pcauto.com.cn',
            'Referer':cur_url,
        }
        url = 'https://bbs.pcauto.com.cn/forum/loadStaticInfos.ajax?isBrandForum=true&tids=%s&fid=%s' % (','.join(tids), cur_url.split('-')[1].split('.')[0])
        try:
            resp = requests.get(url, headers=header, timeout=2)
            jsonline = resp.text
            views = (view.get('view', '') for view in json.loads(jsonline).get('topicViews', [{}]*len(tids)))
        except:
            views = ['']*len(tids)
        return views
            
    def __get_user_car(self, cur_url, tid, fid, vids):
        import requests
        header = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
            'Host':'bbs.pcauto.com.cn',
            'Referer': cur_url
        }
        cookie = {
            'visitedfid':fid
        }
        url = 'https://bbs.pcauto.com.cn/topic/loadStaticInfos.ajax?isBrandForum=true&tid=%s&fid=%s&vids=%s' % (tid, fid, ','.join(vids))
        try:
            resp = requests.get(url, headers=header, cookies=cookie, timeout=2)
            jsonline = resp.text
            cartype = json.loads(jsonline).get('vipInfo', [{}]*len(vids))
        except:
            cartype = [{}]*len(vids)
        return cartype


class SchnitzerSpider(AuDiSpider):  # bmw的改装厂

    name = 'schnitzer'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-20676.html', 
        'https://bbs.pcauto.com.cn/forum-20670.html', 
        'https://bbs.pcauto.com.cn/forum-20685.html', 
        'https://bbs.pcauto.com.cn/forum-20672.html', 
        'https://bbs.pcauto.com.cn/forum-13372.html', 
        'https://bbs.pcauto.com.cn/forum-28992.html', 
        'https://bbs.pcauto.com.cn/forum-28992.html', 
        'https://bbs.pcauto.com.cn/forum-28992.html', 
        'https://bbs.pcauto.com.cn/forum-20671.html'
    ]


class ALPINASpider(AuDiSpider):  # bmw改装厂

    name = 'alpina'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-25315.html', 
        'https://bbs.pcauto.com.cn/forum-24675.html', 
        'https://bbs.pcauto.com.cn/forum-24685.html', 
        'https://bbs.pcauto.com.cn/forum-26327.html'
    ]


class ARCFOXSpider(AuDiSpider):  # 北汽新能源

    name = 'arcfox'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-20849.html', 
        'https://bbs.pcauto.com.cn/forum-24245.html'
    ]


class AlfaRomeoSpider(AuDiSpider):  # 阿尔法罗密欧

    name = 'alfaromeo'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-17247.html', 
        'https://bbs.pcauto.com.cn/forum-17169.html', 
        'https://bbs.pcauto.com.cn/forum-17169.html', 
        'https://bbs.pcauto.com.cn/forum-17169.html', 
        'https://bbs.pcauto.com.cn/forum-17169.html', 
        'https://bbs.pcauto.com.cn/forum-17169.html', 
        'https://bbs.pcauto.com.cn/forum-17169.html', 
        'https://bbs.pcauto.com.cn/forum-17262.html', 
        'https://bbs.pcauto.com.cn/forum-17258.html'
    ]


class AstonMartinSpider(AuDiSpider):  # 阿斯顿马丁
    name = 'astonmartin'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-17267.html', 
        'https://bbs.pcauto.com.cn/forum-17254.html', 
        'https://bbs.pcauto.com.cn/forum-17266.html', 
        'https://bbs.pcauto.com.cn/forum-17272.html', 
        'https://bbs.pcauto.com.cn/forum-17275.html', 
        'https://bbs.pcauto.com.cn/forum-17264.html', 
        'https://bbs.pcauto.com.cn/forum-17279.html', 
        'https://bbs.pcauto.com.cn/forum-17277.html', 
        'https://bbs.pcauto.com.cn/forum-22855.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-17170.html', 
        'https://bbs.pcauto.com.cn/forum-29107.html'
    ]
    

class AiChiSpider(AuDiSpider):  # 爱驰

    name = 'aichi'

    start_urls = [
        'https://bbs.pcauto.com.cn/forum-29097.html', 
        'https://bbs.pcauto.com.cn/forum-29136.html'
    ]