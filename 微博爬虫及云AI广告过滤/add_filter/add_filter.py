#! usr/bin/env python3
# -*- coding: utf-8
# python: v3.7


import os
import base64
import requests
import json
import time
import random


# 读取一张图片
def read_img(file_path):
    with open(file_path, 'rb') as f:
        return f.read()


# 存储一张图片
def storage_img(file_content, file_name, file_path):
    wether_dir(file_path)
    with open(os.path.join(file_path, file_name), 'wb') as f:
        f.write(file_content)


# 图片路径是否存在
def wether_dir(file_path):
    if not os.path.exists(file_path):
        os.makedirs(file_path)


# 对图片进行base64编码
def base64_encode(file_content):
    return base64.standard_b64encode(file_content)


# 从服务器获取token
def get_token_online():
    API_KEY = 'D34fzhCjwI1SiNw1Eiax9fET'
    SECRET_KEY = 'kdv8T9KE2zLhHhR5vSr0hsI4X9YKLkta'
    GET_TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=%s&client_secret=%s' % (API_KEY, SECRET_KEY)
    header = {
        'Content-Type': 'application/json;charset=utf-8'
    }
    resp = requests.post(GET_TOKEN_URL, headers=header)
    jsonline = resp.text
    return json.loads(jsonline).get('access_token', None)


# 获取token接口
def get_token():
    print('获取token...')
    token = wether_token()
    if not token:
        token = get_token_online()
        write_token(token)
    print(token)
    return token


# 读取本地token
def read_token():
    with open('token.json', 'r') as f:
        return json.load(f)


# 将token写入本地
def write_token(token):
    with open('token.json', 'w') as f:
        json.dump(token, f)    


# 本地是否存在token或者是否过期
def wether_token():
    if not os.path.exists('token.json'):
        token = None
    else:
        mtime = os.path.getmtime('token.json')
        if mtime <= 2592000:
            token = read_token()
        else:
            token = None
    return token


# 返回一个识别的结果列表，非空为广告
def get_add_status(file_path_i):
    URL = '	https://aip.baidubce.com/api/v1/solution/direct/img_censor?access_token=%s'
    TOKEN = get_token()
    header = {
        'Content-Type': 'application/json'
    }
    img = read_img(file_path_i)
    bimg = base64_encode(img)
    # print(bimg)
    data = {
        'image': bimg.decode('utf-8'),
        'scenes': ['watermark',],
        'sceneConf': {
            # 'webimage': {},
            # 'ocr': {
            #     'detect_direction': 'false',
            #     'recognize_granularity': 'big',
            #     'language_type': 'CHN_ENG',
            #     'mask': '-'
            # }
        }
    }
    resp = requests.post(URL % TOKEN, headers=header, data=json.dumps(data))
    # print(resp)
    jsonline = json.loads(resp.text)
    print(jsonline)
    return jsonline['result']['watermark']['result'], img


def filter_add(file_path_i, file_path_o_add, file_path_o):
    result, img = get_add_status(file_path_i)
    file_name = os.path.basename(file_path_i)
    if result:
        print(file_name, '识别为广告！')
        storage_img(img, file_name, file_path_o_add)
    else:
        print(file_name, '识别为有价值图片！')
        storage_img(img, file_name, file_path_o)
        


if __name__ == '__main__':
    file_list = os.scandir(r'C:\Users\Administrator\Desktop\weibopider\images')
    for file in file_list:
        filter_add(file.path, os.path.join('C:\\Users\\Administrator\\Desktop\\weibopider\\', 'images_add'), os.path.join('C:\\Users\\Administrator\\Desktop\\weibopider\\', 'images_valuable'))
        time.sleep(1)