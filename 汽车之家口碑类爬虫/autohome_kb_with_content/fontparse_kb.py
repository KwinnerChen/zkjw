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
        (25, 18, '110'): '比',
        (13, 25, 4, 7, 6, 6, '14'): '泥',
        (20, 20, 6, '36'): '近',
        (27, '52'): '七',
        (14, 4, 4, 4, '248'): '自',
        (23, 8, 6, 4, 4, '132'): '响',
        (36, 4, 4, '20'): '有',
        (4, 4, 4, '60'): '三',
        (18, 4, '40'): '五',
        (37, 5, 4, '28'): '皮',
        (32, 12, 4, 7, 4, '32'): '很',
        (16, 14, 7, 6, 6, '50'): '冷',
        (7, 6, 4, 7, '32'): '少',
        (30, '22'): '左',
        (35, 8, 5, 4, 4, 4, 6, 6, '36'): '盘',
        (29, 7, '54'): '长',
        (21, 19, '36'): '无',
        (20, 4, 4, 4, 4, 6, 7, '50'): '真',
        (27, 4, '38'): '右',
        (16, 4, 4, '168'): '中',
        (40, 12, 6, 6, '12'): '低',
        (36, 19, 4, 5, 4, 5, 4, '10'): '硬',
        (12, '52'): '上',
        (24, 4, 4, 4, 4, '34'): '里',
        (14, 26, 4, 4, 6, '114'): '的',
        (34, 20, 4, 6, '24'): '远',
        (8, 17, 6, 10, 4, 4, '40'): '高',
        (17, 6, '12'): '不',
        (16, 16, 34, '24'): '排',
        (18, 6, 6, '110'): '当',
        (54, 4, 4, 4, '24'): '着',
        (25, 11, '12'): '外',
        (61, 35, 7, '22'): '矮',
        (34, 12, 15, 6, 6, '28'): '控',
        (25, 31, 14, 6, '26'): '孩',
        (8, 35, 4, 10, 4, 6, '20'): '短',
        (4, '32'): '一',
        (23, '28'): '大',
        (8, 4, 33, '24'): '和',
        (12, 15, 7, 6, '30'): '空',
        (15, '52'): '下',
        (6, 15, 4, 4, 6, '138'): '问',
        (22, '106'): '了',
        (40, 17, 15, '36'): '软',
        (43, 41, '28'): '耗',
        (27, 28, 7, '36'): '好',
        (8, 25, 12, 4, 4, 7, 6, '26'): '得',
        (7, 6, 13, '36'): '小',
        (28, 25, '26'): '机',
        (27, 4, '40'): '开',
        (11, 7, '18'): '八',
        (24, 15, 6, 6, '36'): '实',
        (4, 6, 7, 6, '54'): '六',
        (12, '50'): '十',
        (8, 30, 4, 4, '14'): '是',
        (38, '32'): '九',
        (17, 20, 6, '38'): '坏',
        (34, 5, 5, 5, 5, 5, '34'): '更',
        (24, 8, 4, 4, 4, 4, 4, 4, 4, '36'): '量',
        (25, 25, '62'): '多',
        (70, '34'): '养',
        (22, 7, 7, '24'): '公',
        (8, 34, 4, '8'): '加',
        (12, 4, 4, 4, 4, 7, 7, 7, '24'): '油',
        (8, 17, 11, 4, 4, '42'): '音',
        (8, 7, 7, 4, '26'): '只',
        (4, 4, '60'): '二',
        (32, 6, 4, '144'): '味',
        (19, 8, 4, 4, '16'): '启',
        (32, 12, 4, '22'): '保',
        (32, 6, 6, '24'): '来',
        (16, 14, 14, '32'): '坐',
        (31, 10, 24, 7, '32'): '级',
        (18, 25, 6, 6, '8'): '档',
        (34, 25, 4, '38'): '动',
        (8, 8, 13, 4, 4, 4, 4, 4, 4, 4, '48'): '副',
        (15, 4, 6, '184'): '门',
        (27, 27, 8, 4, 4, 7, '32'): '路',
        (13, 6, 25, 4, 4, '132'): '呢',
        (37, '44'): '手',
        (32, 11, 7, '24'): '性',
        (35, 4, 4, 4, '44'): '身',
        (29, 6, 6, 6, 6, '52'): '雨',
        (17, 19, 6, 7, '26'): '灯',
        (48, 20, '14'): '地',
        (44, 6, 6, '16'): '光',
        (37, '204'): '内',
        (21, 20, 6, 7, '36'): '过',
        (8, 26, '186'): '四',
        (29, 4, 4, 4, 4, '130'): '电'
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
