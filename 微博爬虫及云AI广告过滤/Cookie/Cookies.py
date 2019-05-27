#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v 3.6.4


from downloader import Downloader


class Cookies():

    cookie = {}
    
    def get_cookie(self, response, mix=True):
        cookie = response.cookies.get_dict()
        if mix:
            self.__cookie_mix(cookie)
        else:
            self.cookie = cookie
        
    def __cookie_mix(self, cookie):
        self.cookie.update(cookie)

    def clear(self):
        self.cookie.clear()


def get_cookie_from_url(url):
    class Mydownloader(Downloader):
        pass
    cookie = Cookies()
    downloader = Mydownloader()
    resp = downloader.get(url)
    cookie.get_cookie(resp)
    return cookie
    

