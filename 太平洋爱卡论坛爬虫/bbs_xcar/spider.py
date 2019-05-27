#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from selector import Selector
from Commons.common import Task, BaseSpider
from urllib.parse import urljoin
from datetime import datetime
from typing import Iterable
import re


class AuDiSpider(BaseSpider):  # 奥迪

    name = 'audi'

    start_urls = [
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=738',
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=739', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=840', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=740', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1947', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1648', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=887', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=741', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1485', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1157', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1158', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=931', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1161', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=589', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=742', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=743', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1984', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=2000', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1350', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=703', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1159', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1160', 
                'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=991'
            ]

    def get_bbs_info_list(self, response):
        selector = Selector(response)
        rela_urls = selector.xpath('//dl[@class="list_dl"]/dt/p[@class="thenomal"]/a[@class="titlink"]/@href')
        urls = map(lambda x: urljoin(selector.url, x), rela_urls)
        rela_next_url_list = ''.join(selector.xpath('//div[@class="table-article bottomfy"]/div[@class="forumList_page"]/a[@class="page_down"]/@href'))
        next_url = urljoin(selector.url, rela_next_url_list)
        next_url = next_url  if rela_next_url_list else ''
        gener_info_url = [Task(url = u, method='get', callback=self.bbs_info_content) for u in urls if u]
        next_url_task = Task(url=next_url, method='get', callback=self.get_bbs_info_list)
        # print(gener_info_url, next_url_task)
        return gener_info_url, next_url_task

    # 最终返回的item必须是一个可迭代的
    def bbs_info_content(self, response):
        selector = Selector(response)
        hfs_djs = ''.join(map(lambda x: x.strip(), selector.xpath('//p[@id="showPic"]//text()')))
        hfs = ''.join(re.findall(r'回复[:：](\d*)', hfs_djs))
        djs = ''.join(re.findall(r'查看[:：](\d*)', hfs_djs))
        bbs_id = ''.join(re.findall(r'tid=(\d+)', response.url))
        bbs_bt = re.sub(r'[>\n\t\r ]+', '', ''.join(map(lambda x: x.strip(), selector.xpath('//h1[@class="title"]/text()'))))
        qa = selector.xpath('//form[@name="poll"]')
        jing = selector.xpath('//span[@class="forum_jing"]')
        bbs_nrs = map(lambda x:tuple(map(lambda s: s.strip(), x)), map(lambda x: x.xpath('.//div[@class="t_msgfont1"]//text()'), selector.xpath('//form[@id="delpost"]/div[@class="F_box_2"]'))) # 先将节点生成列表，再将列表合并为字符串
        bbs_nrs = tuple(map(lambda x: ''.join(x), bbs_nrs))
        sfs_dss_zcrqs_ftzss = tuple(map(lambda s: ''.join(map(lambda y: y.strip(),s)), map(lambda x: x.xpath('./p[last()]//text()'), selector.xpath('//div[@class="smalltxt"]'))))
        sfs = tuple(map(lambda x: ''.join(re.findall(r'来自[：:][ ]*?(\w+)\|', x)), sfs_dss_zcrqs_ftzss))
        dss = tuple(map(lambda x: ''.join(re.findall(r'来自[：:].*?\|(\w+)', x)), sfs_dss_zcrqs_ftzss))
        zcrqs = tuple(map(lambda x: ''.join(re.findall(r'注册[：:][ ]*?([\d\-]+)', x)), sfs_dss_zcrqs_ftzss))
        ftzss = tuple(map(lambda x: ''.join(re.findall(r'帖子[:：](\d+)', x)), sfs_dss_zcrqs_ftzss))
        ftsjs = map(lambda x:map(lambda s: s.strip(), x), map(lambda x: x.xpath('.//div[@style="padding-top: 4px;float:left"]/text()'), selector.xpath('//form[@id="delpost"]/div[@class="F_box_2"]')))
        ftsjs = map(lambda x: ''.join(x), ftsjs)
        ftsjs = map(lambda x: ''.join(re.findall(r'\d{2,4}\-\d{1,2}\-\d{1,2} \d{1,2}:\d{1,2}', x)), ftsjs)
        # ftsjs = tuple(map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M') if x else '0001-01-01 01:01:01', ftsjs))
        yhid = tuple(map(lambda x: ''.join(map(lambda s: ''.join(re.findall(r'uid=(\d+)', s)), x)), map(lambda x: x.xpath('.//td[@class="t_user"]/a[@class="bold"]/@href'), selector.xpath('//form[@id="delpost"]/div[@class="F_box_2"]'))))
        imgs = tuple(map(lambda x:', '.join(map(lambda s: s.strip(), x)), map(lambda x: x.xpath('.//div[@class="t_msgfont1"]//img/@src'), selector.xpath('//form[@id="delpost"]/div[@class="F_box_2"]'))))
        yhm = tuple(map(lambda x:', '.join(map(lambda s: s.strip(), x)), map(lambda x: x.xpath('.//td[@class="t_user"]/a/text()'), selector.xpath('//form[@id="delpost"]/div[@class="F_box_2"]'))))
        craw_time = datetime.now()
        tablename = ''.join(selector.xpath('//h1[@class="title"]/a/text()')).replace('论坛', '')
        next_page_part = ''.join(selector.xpath('//div[@class="FpageNum tzy_list"]//a[@class="page_down"]/@href'))
        next_page = urljoin(selector.url, next_page_part) if next_page_part else ''
        info_dict_tuple = zip(bbs_nrs, sfs, dss, zcrqs, ftzss, ftsjs, yhid, imgs, yhm)
        dict_list = []
        for i in info_dict_tuple:
            item = dict.fromkeys(set(self.data_struct), '')
            item['BBS_ID'] = int(bbs_id)
            item['BBS_BT'] = bbs_bt
            item['BBS_QA'] = '1' if qa else '0'
            item['BBS_JING'] = '1' if jing else '0'
            item['BBS_NR'] = i[0]
            item['BBS_SF'] = i[1]
            item['BBS_DS'] = i[2]
            item['BBS_FTSJ'] = i[5]
            item['BBS_HFS'] = hfs
            item['BBS_DJS'] = djs
            item['BBS_YHID'] = i[6]
            item['BBS_ZCRQ'] = i[3]
            item['BBS_IMG'] = i[7]
            item['BBS_YHM'] = i[8]
            item['BBS_FTZS'] = i[4]
            item['BBS_TABLENAME'] = tablename
            item['CRAW_TIME'] = craw_time
            dict_list.append(item)
        return Task(url=next_page, method='get', item=dict_list, callback=self.bbs_info_content)


class CherySpider(AuDiSpider):  # 奇瑞

    name = 'chery'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1483',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1604',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1576',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1057',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=2243',
    ]


class SuzukiSpider(AuDiSpider):  # 铃木

    name = 'suzuki'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=637',
    ]


class HondaSpider(AuDiSpider):  # 本田

    name = 'honda'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=439',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=968',
    ]


class MazidaSpider(AuDiSpider):  # 马自达

    name = 'mazida'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1150',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1056'
    ]


class BuickSpider(AuDiSpider):  # 别克

    name = 'buick'
    
    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=974',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1143',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=735',
    ]


class DongfengSpider(AuDiSpider):  # 东风

    name = 'dongfeng'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=648',
    ]


class CitroenSpider(AuDiSpider):  # 雪铁龙

    name = 'citroen'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=541',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1068',
    ]


class HaimaSpider(AuDiSpider):  # 海马

    name = 'haima'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=960',
    ]


class ChevroletSpider(AuDiSpider):  # 雪佛兰

    name = 'chevrolet'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=640',
    ]


class AlfaromeoSpider(AuDiSpider):  # 阿尔法罗密欧

    name = 'alfaromeo'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=540',
    ]


class AstonMartinSpider(AuDiSpider):  # 阿斯顿马丁

    name = 'astonmartin'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=874',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1162',
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1163',
    ]


class MitsubishiSpider(AuDiSpider):  # 三菱汽车

    name = 'mitsubishi'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=845',

    ]


class ToyotaSpider(AuDiSpider):  # 丰田

    name = 'toyota'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=867', 
    ]


class DasAutoSpider(AuDiSpider):  # 大众

    name = 'dasauto'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1502',
    ]


class SubaruSpider(AuDiSpider):  # 斯巴鲁
    
    name = 'subaru'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=736',
    ]


class KIASpider(AuDiSpider):  # 起亚

    name = 'kia'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1541',
    ]


class JiuLongSpider(AuDiSpider):  # 九龙

    name = 'jiulong'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=1654',
    ]


class AiChiSpider(AuDiSpider):  # 爱驰

    name = 'aichi'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=2167',
    ]


class BMWSpider(AuDiSpider):  # 宝马
    
    name = 'bmw'

    start_urls = [
        'http://www.xcar.com.cn/bbs/forumdisplay.php?fid=744'
    ]