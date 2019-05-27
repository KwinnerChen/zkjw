#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from lxml import etree
import re

class Selector():
    def __init__(self, response, encoding=None):
        self.response = response
        if encoding:
            self.response.encoding = encoding
        else:
            response.encoding = response.apparent_encoding
        self.tree = etree.HTML(response.text)

    @property
    def url(self):
        return self.response.url

    @property
    def cookies(self):
        return self.response.cookies.get_dict()

    def xpath(self, xpath_exe):
        return self.tree.xpath(xpath_exe)

    def refresh(self, response):
        self.response = response
        response.encoding = response.apparent_encoding
        self.tree = etree.HTML(response.text)

    def search(self, reg_exp, string='', **kwargs):
        string = string if string else self.response.text
        re_obj = re.search(reg_exp, string, **kwargs)
        return re_obj

    def findall(self, reg_exp, string='', **kwargs):
        string = string if string else self.response.text
        return re.findall(reg_exp, string, **kwargs)
        