#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from lxml import etree
from requests import Response
import re

class Selector():
    def __init__(self, response, encoding=None):
        if isinstance(response, Response):
            self.response = response
            if encoding:
                self.response.encoding = encoding
            else:
                self.response.encoding = response.apparent_encoding
            self.tree = etree.HTML(response.text)
            self.encoding = encoding
        elif isinstance(response, str):
            self.tree = etree.HTML(response)

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
        string = string or self.response.text
        re_obj = re.search(reg_exp, string, **kwargs)
        return re_obj

    def findall(self, reg_exp, string='', **kwargs):
        string = string or self.response.text
        return re.findall(reg_exp, string, **kwargs)

    def get_html(self, xpath_exe):
        html_ = self.tree.xpath(xpath_exe)[0] or ''
        html = etree.tostring(html_, encoding=self.encoding or 'utf-8').decode(encoding=self.encoding or 'utf-8')
        return html
    
    def json(self, **kwargs):
        return self.response.json(**kwargs)
        