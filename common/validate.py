#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/4/7 00:49
# author: fengqiyuan
from datetime import datetime


def check_dict(d, required_keys):
    return all(key in d and d[key] for key in required_keys)


def is_valid_datetime(datetime_str, format='%Y-%m-%d %H:%M:%S'):
    try:
        datetime.strptime(datetime_str, format)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    print(is_valid_datetime('2023-04-11 09:11:11'))
    print(is_valid_datetime('2023-04-11'))
    print(is_valid_datetime('2023-04-11 09:11:11.001'))
    print(is_valid_datetime('2023-04-11 09:11'))
    print(is_valid_datetime('2023-04-11T09:11'))
