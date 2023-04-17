#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/17 19:46
# author: fengqiyuan
import json
import urllib
import urllib.parse
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from common.logger import logger


def send_request(method, url, headers=None, params=None, data=None, files=None):
    json_data = None
    new_data = None
    content_type = headers.get('Content-Type') if headers else None

    if data and isinstance(data, dict):
        if not content_type:
            new_data = json.dumps(data)
        elif content_type == 'application/json':
            json_data = data
        elif content_type == 'application/x-www-form-urlencoded':
            new_data = urllib.parse.urlencode(data)
        elif content_type == 'multipart/form-data':
            new_data = MultipartEncoder(fields=data)
            headers['Content-Type'] = new_data.content_type
    elif data and isinstance(data, str):
        try:
            new_data = json.loads(data)
            if not content_type:
                json_data = new_data
            elif content_type == 'application/json':
                json_data = new_data
            elif content_type == 'application/x-www-form-urlencoded':
                new_data = urllib.parse.parse_qs(new_data)
            elif content_type == 'multipart/form-data':
                new_data = MultipartEncoder(fields=new_data)
                headers['Content-Type'] = new_data.content_type
        except ValueError as e:
            logger.info(f"该字符串不能转成JSON对象, 错误信息:{str(e)}")
    elif data and isinstance(data, bytes):
        try:
            new_data = json.loads(data.decode('utf-8'))
            if not content_type:
                json_data = new_data
            elif content_type == 'application/json':
                json_data = new_data
            elif content_type == 'application/x-www-form-urlencoded':
                new_data = urllib.parse.parse_qs(new_data)
            elif content_type == 'multipart/form-data':
                new_data = MultipartEncoder(fields=new_data)
                headers['Content-Type'] = new_data.content_type
        except ValueError as e:
            logger.info(f"该二进制数据不能转成JSON对象, 错误信息:{str(e)}")
    new_data = new_data if new_data else data
    if json_data:
        response = requests.request(method, url, headers=headers, params=params, json=json_data)
    else:
        response = requests.request(method, url, headers=headers, params=params, data=new_data, files=files)
    return response


if __name__ == '__main__':
    pass
