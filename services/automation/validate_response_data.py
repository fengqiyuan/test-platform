#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/4/4 14:57
# author: fengqiyuan
import jsonschema
from common.logger import logger


def validate_response_data(validate_type, expected_data, actual_data, result):
    # result = {'execute_status': 0, 'actual_result': {'message': ''}}
    if validate_type == 'full_match':
        check_expected_data(expected_data, actual_data, True, result)
    elif validate_type == 'partial_match':
        check_expected_data(expected_data, actual_data, False, result)
    elif validate_type == 'jsonschema':
        if isinstance(actual_data, (dict, list)):
            try:
                jsonschema.validate(actual_data, expected_data)
            except jsonschema.exceptions.ValidationError as e:
                result['execute_status'] = 0
                result['actual_result']['message'] += f"JSON schema 验证失败: {str(e)}\n"
        elif actual_data != expected_data:
            result['execute_status'] = 0
            result['actual_result']['message'] += f"JSON schema 验证失败\n"
    elif validate_type == 'specified_fields':
        if isinstance(actual_data, dict):
            expected_data_dict = {}
            for item in expected_data.split('\n'):
                key, value = item.split('=' or ':')
                expected_data_dict[key] = value
            check_expected_data(expected_data_dict, actual_data, False, result)
        elif isinstance(actual_data, list):
            expected_data_list = []
            for item1 in expected_data.split('\n'):
                for item2 in item1.split(','):
                    expected_data_dict = {}
                    key, value = item2.split('=' or ':')
                    expected_data_dict[key] = value
                    expected_data_list.append(expected_data_dict)
            check_expected_data(expected_data_list, actual_data, False, result)
        elif actual_data != expected_data:
            result['execute_status'] = 0
            result['actual_result']['message'] += "指定字段验证失败\n"
    else:
        result['execute_status'] = 0
        result['actual_result']['message'] += f'无效的验证类型: {validate_type}\n'


def check_expected_data(expected_data, actual_data, is_equal, result):
    if isinstance(expected_data, list) and isinstance(actual_data, list):
        if is_equal and len(expected_data) != len(actual_data):
            result['execute_status'] = 0
            result['actual_result']['message'] += f'期望值{expected_data}与实际值{actual_data}长度不一致\n'
        for item1, item2 in zip(expected_data, actual_data):
            if isinstance(item1, list) and isinstance(item2, list):
                check_expected_data(item1, item2, is_equal, result)
            elif isinstance(item1, dict) and isinstance(item2, dict):
                check_expected_data(item1, item2, is_equal, result)
            elif isinstance(item1, (str, int, float, bool, type(None))) \
                    and isinstance(item2, (str, int, float, bool, type(None))):
                if item1 != item2:
                    result['execute_status'] = 0
                    result['actual_result']['message'] += f'期望值{item1}不等于实际值{item2}\n'
            else:
                result['execute_status'] = 0
                result['actual_result']['message'] += f'期望值{item1}与实际值{item2}类型不一致\n'
    elif isinstance(expected_data, dict) and isinstance(actual_data, dict):
        if is_equal:
            if len(expected_data) != len(actual_data):
                result['execute_status'] = 0
                result['actual_result']['message'] += f'期望值{expected_data}与实际值{actual_data}长度不一致\n'
            for (key1, value1), (key2, value2) in zip(expected_data.items(), actual_data.items()):
                if key1 != key2:
                    result['execute_status'] = 0
                    result['actual_result']['message'] += f'{key1}期望值与{key2}实际值键不一致\n'
                    continue
                if isinstance(value1, list) and isinstance(value2, list):
                    check_expected_data(value1, value2, is_equal, result)
                elif isinstance(value1, list) and isinstance(value2, list):
                    check_expected_data(value1, value2, is_equal, result)
                elif isinstance(value1, (str, int, float, bool, type(None))) \
                        and isinstance(value2, (str, int, float, bool, type(None))):
                    if value1 != value2:
                        result['execute_status'] = 0
                        result['actual_result']['message'] += f'{key1}期望值{value1}不等于实际值{value2}\n'
                else:
                    result['execute_status'] = 0
                    result['actual_result']['message'] += f'{key1}期望值{value1}与{key2}实际值{value2}类型不一致\n'
        else:
            for key1, value1 in expected_data.items():
                if key1 not in actual_data.keys():
                    result['execute_status'] = 0
                    result['actual_result']['message'] += f'{key1}期望值在实际值中不存在\n'
                    continue
                if isinstance(value1, list) and isinstance(actual_data[key1], list):
                    check_expected_data(value1, actual_data[key1], is_equal, result)
                elif isinstance(value1, dict) and isinstance(actual_data[key1], dict):
                    check_expected_data(value1, actual_data[key1], is_equal, result)
                elif isinstance(value1, (str, int, float, bool, type(None))) \
                        and isinstance(actual_data[key1], (str, int, float, bool, type(None))):
                    if value1 != actual_data[key1]:
                        result['execute_status'] = 0
                        result['actual_result']['message'] += f'{key1}期望值{value1}不等于实际值{actual_data[key1]}\n'
                else:
                    result['execute_status'] = 0
                    result['actual_result']['message'] += f'{key1}期望值{value1}与实际值{actual_data[key1]}类型不一致\n'

    elif isinstance(expected_data, (str, int, float, bool, type(None))) \
            and isinstance(actual_data, (str, int, float, bool, type(None))):
        if is_equal:
            if expected_data != actual_data:
                result['execute_status'] = 0
                result['actual_result']['message'] += f'期望值{expected_data}不等于实际值{actual_data}\n'
        else:
            if actual_data.find(expected_data) < 0:
                result['execute_status'] = 0
                result['actual_result']['message'] += f"{actual_data}部分匹配验证失败\n"
    else:
        result['execute_status'] = 0
        result['actual_result']['message'] += f'期望值与实际值{actual_data}类型不一致\n'
