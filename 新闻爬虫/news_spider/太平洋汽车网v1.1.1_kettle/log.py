#! usr/bin/env python3
# -*- coding: utf-8 -*-
# author: Kwinner Chen
# python: v 3.6.4


import logging


def log(logfilename):
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG)
    handler = logging.FileHandler(logfilename, encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s    %(message)s')
    handler.setFormatter(fmt=formatter)
    logger.addHandler(handler)
    shander = logging.StreamHandler()
    shander.setLevel(logging.DEBUG)
    sformatter = logging.Formatter('%(asctime)s    %(message)s')
    shander.setFormatter(sformatter)
    logger.addHandler(shander)
    return logger
