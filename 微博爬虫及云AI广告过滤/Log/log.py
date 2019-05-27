#! usr/bin/env python3
# -*- coding: utf-8 -*-
# python: v3.6.4


import logging
import os

file_path = os.path.dirname(os.path.abspath(__file__))

def get_a_logger(log_name):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(os.path.join(file_path, log_name), encoding='utf-8')
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s    %(message)s')
    handler.setFormatter(formatter)
    stream = logging.StreamHandler()
    stream.setLevel(logging.INFO)
    stream.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(stream)
    return logger
