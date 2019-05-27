#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


import requests
from selector import Selector
from urllib.parse import urljoin


def get_url_list_page(url):
    return requests.get(url, headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0'})


def page_parse(response):
    selector = Selector(response)
    car_brands = selector.xpath('//div[@id="data-A"]/p/em/a/text()')
    car_types_url = [[urljoin(selector.url, url) for url in urls.xpath('./i/span/a/@href')] for urls in selector.xpath('//div[@id="data-A"]/p')]
    car_dict = dict(zip(car_brands, car_types_url))
    return car_dict


if __name__ == '__main__':
    resp = get_url_list_page('https://bbs.pcauto.com.cn/#')
    car_dict = page_parse(resp)
    print(car_dict)