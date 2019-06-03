#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


from fontTools.ttLib import TTFont
from lxml import etree
from urllib.parse import urljoin, urlsplit
from io import BytesIO
import re
import requests


class FontParse():

    # 字体与点数
    font_map = {
       
    }

    def __init__(self, response):
        self.response = response
        self.__open_ttf()

    def __get_ttf_url(self):  # 获取字体文件地址
        html = self.response.text
        ttf_url = ''.join(re.findall(r"url\('(//.*?ttf)'", html))
        ttf_url = urljoin(self.response.url, ttf_url) if ttf_url else ''
        return ttf_url

    def __get_ttf(self):  # 将字体文件字节码写到缓存
        url = self.__get_ttf_url()
        if url:
            header = {
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
                'Host':urlsplit(url).netloc
            }
            resp = requests.get(url, headers=header)
            return BytesIO(resp.content)

    def __open_ttf(self):
        f = self.__get_ttf()
        self.font = TTFont(f)
        f.close()
        del f

    def __saveXML(self):  # 将字体文件转换为可读的xml文件，写入缓存
        f = BytesIO()
        self.font.saveXML(f)
        return f

    def __get_codename_ptnum_map(self):  # 获取字体编码名与字体点阵的映射关系，编码名编码为utf-8字节码
        f = self.__saveXML()
        tree = etree.XML(f.getvalue())
        f.close()
        del f
        codename = [eval('"\\u'+i[3:].lower()+'"').encode('utf-8') for i in tree.xpath('//TTGlyph[position()>1]/@name') if isinstance(i, str)]
        ptnum = [tuple([len(i.xpath('./pt')) for i in node.xpath('./contour')] + tree.xpath('//mtx[@name="%s"]/@lsb'%node.xpath('@name')[0])) for node in tree.xpath('//TTGlyph[position()>1]')]
        new_dict = dict(zip(codename, ptnum))
        return new_dict

    def get_font_map(self):  # 转化为编码与字体的映射关系
        codename_ptnum_map = self.__get_codename_ptnum_map()
        new_dict = {}
        for k,v in codename_ptnum_map.items():
            new_dict[k] = self.font_map.get(v, '')
        return new_dict

    def turn2font(self):  # 将文本中的字体编码替换为真是的字体，注意编码转换
        font_dict = self.get_font_map()
        html = self.response.text
        tree = etree.HTML(html)
        content_list = [i.encode('utf-8') for i in tree.xpath('//div[@class="matter"]//text()') if not re.search(r'[\r\n ]+', i)]
        content_utf8 = ''.encode('utf-8').join(content_list)
        for k, v in font_dict.items():
            content_utf8 = content_utf8.replace(k, v.encode('utf-8'))
        return content_utf8.decode('utf-8')

    def string2font(self, string):
        font_dict = self.get_font_map()
        string_utf8 = string.encode('utf-8')
        for k, v in font_dict.items():
            string_utf8 = string_utf8.replace(k, v.encode('utf-8'))
        return string_utf8.decode('utf-8')
