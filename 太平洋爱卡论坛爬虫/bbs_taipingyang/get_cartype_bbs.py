#! usr/bin/env python3
# -*- coding: utf-8 -*-


from downloader import Downloader
from datetime import datetime
from lxml import etree

mydownloader = Downloader()
resp_with_cookie = mydownloader.get('http://www.xcar.com.cn/bbs/header/bbsnav.htm?action=bbsnav&domain=club.xcar.com.cn&v=%s'%datetime.now().strftime('%Y%m%d%H%M'))
cookie = resp_with_cookie.cookies.get_dict()
mydownloader.set_cookie(cookie)
resp = mydownloader.get('http://club.xcar.com.cn/')
html = resp.text
tree = etree.HTML(html)

bbs_cartype_nodes = tree.xpath('//div[@id="quick_index_content"]//li/em/a')
print(list(map(lambda y: ''.join(y.xpath('./@href')), filter(lambda x: '奥迪' in ''.join(x.xpath('./text()')), bbs_cartype_nodes))))
