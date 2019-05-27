#!/user/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/9/14 16:04
# @Author   : zequan.shao
# @File     : seleSpider.py
# @Software : PyCharm

from selenium import webdriver


class SeleSpider:

    def __init__(self):
        self.driver_path = r'F:\zkjw\code\beiqi\Application\chromedriver.exe'
        self.chrome_option = ''

    def _create_driver(self):
        return webdriver.Chrome(self.driver_path)

    def request_page(self, url):
        driver = self._create_driver()
        driver.get(url)

        content_divs = driver.find_elements_by_xpath('//*[@id="listContent"]//div')


    def loop_span(self):
        pass