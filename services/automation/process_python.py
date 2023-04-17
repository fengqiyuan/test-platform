#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/31 19:57
# author: fengqiyuan
import ast
from collections import Counter
from flask import current_app
from flask_caching import Cache
from sqlalchemy import URL, create_engine, text
from sqlalchemy.orm import Session, sessionmaker


def execute_code(exec_python, db_config, redis_config, result):
    python_script = exec_python.get('python_script', '')
    expected_result = exec_python.get('expected_result', {})
    if not python_script:
        return
    validate_input(python_script)
    global_namespace = {'text': text, 'print': print}
    # db_config = {
    #     'drivername': 'mysql+pymysql',
    #     'username': 'root',
    #     'password': '123456',
    #     'host': '192.168.31.143',
    #     'port': '3306',
    #     'database': 'test_platform'
    # }
    # create database engine
    db_url = URL.create(**db_config)
    engine = create_engine(db_url)
    # redis_config = {
    #     'CACHE_TYPE': 'RedisCache',
    #     'CACHE_REDIS_HOST': '192.168.31.143',
    #     'CACHE_REDIS_PORT': "6379",
    #     'CACHE_REDIS_DB': 0,
    #     'CACHE_DEFAULT_TIMEOUT': 300
    # }
    cache = Cache()
    cache.init_app(current_app, config=redis_config)
    global_namespace['cache'] = cache
    Session = sessionmaker(engine)
    with Session() as session:
        global_namespace['session'] = session
        exec(python_script, global_namespace)
    validate_result(expected_result, global_namespace, result)


def execute_python_script(exec_python, engine, cache, result):
    python_script = exec_python.get('python_script', '')
    expected_result = exec_python.get('expected_result', {})
    if not python_script:
        return
    validate_input(python_script)
    global_namespace = {'text': text, 'print': print, 'cache': cache}
    with Session(engine) as session:
        global_namespace['session'] = session
        exec(python_script, global_namespace)
    validate_result(expected_result, global_namespace, result)


def validate_input(python_script):
    try:
        parsed = ast.parse(python_script)
    except SyntaxError:
        raise ValueError("Invalid input code")

    allowed_modules = ['json', 'sqlalchemy', 'datetime', 'redis', 'flask_caching']
    allowed_functions = ['loads', 'dumps', 'func', 'select', 'update', 'delete', 'text', 'print', 'type']
    for node in ast.walk(parsed):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name not in allowed_modules:
                    raise ValueError(f"Module {alias.name} not allowed")
        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                continue
            if node.func.id not in allowed_functions:
                raise ValueError(f"Function {node.func.id} not allowed")


def validate_result(expected_result, global_namespace, result):
    if not expected_result:
        return
    for key, value in expected_result.items():
        if isinstance(value, dict) and isinstance(global_namespace[key], dict):
            if Counter(value) != Counter(global_namespace[key]):
                result['execute_status'] = 0
                result['actual_result']['message'] += "Python脚本验证失败\n"
        elif isinstance(value, list) and isinstance(global_namespace[key], list):
            if value != global_namespace[key]:
                result['execute_status'] = 0
                result['actual_result']['message'] += "Python脚本验证失败\n"
        elif isinstance(value, (str, int, float, bool, type(None))) \
                and isinstance(global_namespace[key], (str, int, float, bool, type(None))):
            if value != global_namespace[key]:
                result['execute_status'] = 0
                result['actual_result']['message'] += f'{key}期望值{value}不等于实际值{global_namespace[key]}\n'
        else:
            result['execute_status'] = 0
            result['actual_result']['message'] += f'{key}期望值{value}与实际值{global_namespace[key]}类型不一致\n'


if __name__ == '__main__':
    print(type(None))
