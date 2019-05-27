#! usr/bin/env python3
# -*- coding: utf-8 -*-


import re
from lxml.etree import HTML


def get_url_jobinfo(html):
    if html:
        tree = HTML(html)
        try:
            uls = tree.xpath('//ul[@id="list_con"]/li')
            url = map(lambda x: x.xpath('.//a/@href')[0], uls)
            return url
        except:
            return None
    else:
        return None


def parse_total_page(html):
    if html:
        tree = HTML(html)
        total_page = tree.xpath('//span[@class="total_page"][1]/text()')
        if total_page:
            total_page = int(total_page[0])
            return total_page
    else:
        return None


def jobinfo_parse(area, html):
    infodict = {}
    if html:
        tree = HTML(html)
        
        job_id = re.search(r'"@id": "https?://.*?/(\d+?x).shtml', html)
        # job_id = re.search(r'psid=(\d+?)&', html)
        if job_id:
            infodict['job_id'] = job_id.group(1)

        job_fbsj = re.search(r'"upDate":"([\d-]+)T', html)
        if job_fbsj:
            infodict['job_fbsj'] = job_fbsj.group(1)

        infodict['data_source'] = '%s.58.com' % area

        job_bt = tree.xpath('//span[@class="pos_title"]/text()')
        if job_bt:
            infodict['job_bt'] = job_bt[0].strip()

        yx = tree.xpath('//span[@class="pos_salary"]/text()')
        if yx:
            infodict['job_yx'] = yx[0].strip()
        yx = tree.xpath('//span[@class="pos_salary daiding"]/text()')
        if yx:
            infodict['job_yx'] = yx[0].strip()

        job_gznx = tree.xpath('//span[@class="item_condition border_right_None"]/text()')
        if job_gznx:
            infodict['job_gznx'] = job_gznx[0].strip()

        job_rs = tree.xpath('//span[@class="item_condition pad_left_none"]/text()')
        if job_rs:
            infodict['job_rs'] = job_rs[0].strip()

        zpdd = map(lambda x: x.strip(), tree.xpath('//div[@class="pos-area"]//text()'))
        infodict['job_zpdd'] = ''.join(zpdd).split('查看地图')[0]

        job_xl = tree.xpath('//span[@class="item_condition"]/text()')
        if job_xl:
            infodict['job_xl'] = job_xl[0].strip()

        infodict['job_zwms'] = ''.join(tree.xpath('//div[@class="des"]//text()'))
        infodict['job_gsmc'] = ''.join(tree.xpath('//div[@class="baseInfo_link"]//text()'))
        infodict['job_company'] = ''.join(map(lambda x: x.strip(), tree.xpath('//div[@class="shiji"]//text()')))

        job_gsgm = tree.xpath('//p[@class="comp_baseInfo_scale"]/text()')
        if job_gsgm:
            infodict['job_gsgm'] = job_gsgm[0].strip()

        job_gshy = tree.xpath('//a[@class="comp_baseInfo_link"]/text()')
        if job_gshy:
            infodict['job_gshy'] = job_gshy[0].strip()
            infodict['hybq'] = infodict['job_gshy']

        job_gszy = tree.xpath('//div[@class="baseInfo_link"]/a/@href')
        if job_gszy:
            infodict['job_gszy'] = job_gszy[0]

        gsfls = tree.xpath('//div[@class="pos_welfare"]/span/text()')
        for i in range(len(gsfls)):
            infodict['job_gsfl%s' % (i+1)] = gsfls[i]      

        return infodict
    else:
        return infodict
