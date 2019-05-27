#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from selector import Selector
from Commons.common import Task
from urllib.parse import urljoin
from lxml import etree
from functools import reduce
from Commons.common import BaseSpider
import re, os, json
import demjson


class Spider(BaseSpider):

    name = 'weibo'

    start_urls = [
        'https://s.weibo.com/weibo/豪华?topnav=1&wvr=6&b=1&page=1',  # 关键字为豪华，大气，舒适
        'https://s.weibo.com/weibo/大气?topnav=1&wvr=6&b=1&page=1',
        'https://s.weibo.com/weibo/舒适?topnav=1&wvr=6&b=1&page=1',
    ]

    def response_parse(self, response):
        selector = Selector(response)
        user_names = selector.xpath('//div[@class="card-feed"]//div[@class="info"]/div[last()]/a[1]/text()')
        user_hrefs = tuple(map(lambda x: urljoin(selector.url, x)+'&is_hot=1', selector.xpath('//div[@class="card-feed"]//div[@class="info"]/div[last()]/a[1]/@href')))
        user_post_texts = tuple(map(lambda y: ''.join((z.strip() for z in y)), map(lambda x: x.xpath('./p//text()'), selector.xpath('//div[@class="card-feed"]/div[@class="content"]'))))
        user_post_imgurls =  tuple(map(lambda x: x.xpath('.//ul[@class="m4"]/li/img/@src'), selector.xpath('//div[@class="card-feed"]/div[@class="content"]')))
        next_page = urljoin(response.url, ''.join(selector.xpath('//a[@class="next"]/@href')))
        user_tumple = zip(user_names, user_hrefs, user_post_texts, user_post_imgurls)
        img_tasks = (Task(url=urljoin('https://', img), method='get', callback=self.img_storage)  for img in reduce(lambda x, y: x+y, user_post_imgurls) if img)
        user_tasks = (Task(url=t[1], method='get', callback=self.user_info, temp=t) for t in user_tumple if t[3])
        next_task = Task(url=next_page, method='get', callback=self.response_parse)
        # print(list(img_tasks))
        return user_tasks, img_tasks, next_task
        
    def img_storage(self, response):
        img_content = response.content
        print('获取到图片内容!')
        file_path = os.path.join(os.curdir, 'images')
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = os.path.basename(response.url)
        with open(os.path.join(file_path, file_name), 'wb') as f:
            f.write(img_content)
            print('图片%s存储到%s' % (file_name, file_path))

    def user_info(self, response, temp):
        item = {}
        # print('用户主页提取到内容%s' % str(temp))
        item['user_name'] = temp[0]
        item['user_host'] = temp[1]
        item['user_post_texts'] = temp[2]
        item['user_post_images'] = [os.path.basename(img) for img in temp[3]]
        selector = Selector(response)
        page_id = selector.search(r"\$CONFIG\['page_id'\]='([\w\d]+?)'")
        if page_id:
            page_id = page_id.group(1)
            user_info_url = 'https://weibo.com/p/%s/info?mod=pedit_more' % page_id
            return Task(url=user_info_url, method='get', callback=self.info, temp=item)

    def info(self, response, temp):
        item = temp
        selector = Selector(response)
        script_line = ''.join(selector.xpath('''//script[contains(text(), '"domid":"Pl_Official_PersonalInfo__57"')]/text()'''))
        jsonline = ''.join(re.findall(r'FM.view\((.*)\)', script_line))
        if jsonline:
            jsonline = demjson.decode(jsonline)
            html = jsonline['html']
            tree = etree.HTML(html)
            user_info = tuple(map(lambda x: (''.join(y.replace('：', '') for y in x.xpath('./span[1]/text()')), ' '.join(z.strip() for z in x.xpath('./span[2]//text()'))), tree.xpath('//li[@class="li_1 clearfix"]')))
            item.update(dict(user_info))
            print('最终信息为%s' % item)
            with open('user_info.txt', 'a', encoding='utf-8') as f:
                f.write(str(item)+'\n')