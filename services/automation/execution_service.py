#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:55
# author: fengqiyuan
import copy
import json
import re
import time
from collections import Counter
from datetime import datetime

import requests
import jsonschema
from flask_caching import Cache
from jsonpath_ng import parse
import concurrent.futures
from flask import jsonify, current_app
from sqlalchemy import URL, create_engine

from common.request import send_request
from common.logger import logger
from common.validate import check_dict
from models.analytics.report import Report
from models.config.environment import Environment
from services.automation.process_python import execute_code, execute_python_script
from services.automation.process_sql import execute_query
from services.automation.runner_service import RunnerService
from services.automation.validate_response_data import validate_response_data
from services.testmgmt.testcase_service import TestCaseService
from models.analytics.result import Result
from models.testmgmt.testcase import TestCase
from exts import cache, env_cache


class ExecutionService:

    def __init__(self, env, runner=None, testsuite=None, user=None):
        self.env = env
        self.user = user if user else {}
        self.testsuite = testsuite if testsuite else {}
        self.runner = runner if runner else {}
        if self.env and self.env.db_config:
            db_url = URL.create(**self.env.db_config)
            self.engine = create_engine(db_url)
        if self.env and self.env.redis_config:
            env_cache.init_app(current_app, config=self.env.redis_config)
            self.cache = env_cache

    def debug_testcase(self, testcase):
        # 必填字段判断
        required_keys = ['test_content', 'expected_result']
        test_content_required_keys = ['method', 'path']
        expected_result_required_keys = ['validate_type', 'expected_status', 'expected_data']
        if not check_dict(testcase, required_keys) or \
                not check_dict(testcase['test_content'], test_content_required_keys) or \
                not check_dict(testcase['expected_result'], expected_result_required_keys):
            return jsonify(errcode=1, execute_status=0, message='缺少必填数据')
        try:
            # 初始化测试结果和执行状态（0 失败 1 成功 2 跳过）
            results = []
            execute_status = 1
            test_data = testcase.get('test_data', None)
            testcases = []
            if isinstance(test_data, dict):
                self.process_data(testcase, test_data)
                testcases.append(testcase)
            elif isinstance(test_data, list):
                for item in test_data:
                    testcase_copy = copy.deepcopy(testcase)
                    self.process_data(testcase_copy, item)
                    testcases.append(testcase_copy)
            else:
                testcases.append(testcase)
            for item in testcases:
                method = item['test_content']['method']
                path = self.env.env_url + item['test_content']['path']
                params = item['test_content'].get('params', {})
                headers = item['test_content'].get('headers', {})
                data = item['test_content'].get('data', {})
                # 发送请求
                response = send_request(method, path, headers, params, data)
                # 验证期望结果和后置处理
                post_process = item.get('post_process', {})
                result = self.validate(response, item['expected_result'], post_process)
                results.append(result)
                # 处理所有测试的最终执行状态
                execute_status = execute_status and result['execute_status']
            logger.info(f"所有验证结果: {results}")
            if execute_status:
                return jsonify(errcode=0, execute_status=execute_status, results=results)
            else:
                return jsonify(errcode=1, execute_status=execute_status, results=results)
        except Exception as e:
            logger.error(str(e))
            return jsonify(errcode=1, execute_status=0, message=str(e)), 500

    def execute_testcase(self, testcase, app=None):
        app = app if app else current_app
        with app.app_context():
            print(current_app.name)
            # 必填字段判断
            testcase_id = testcase.get('testcase_id', None)
            required_keys = ['test_content', 'expected_result']
            test_content_required_keys = ['method', 'path']
            expected_result_required_keys = ['validate_type', 'expected_status', 'expected_data']
            if not check_dict(testcase, required_keys) or \
                    not check_dict(testcase['test_content'], test_content_required_keys) or \
                    not check_dict(testcase['expected_result'], expected_result_required_keys):
                return {'testcase_id': testcase_id, 'execute_status': 2, 'actual_result': {'message': '缺少必填数据'}}
            try:
                # 初始化测试结果和执行状态（0 失败 1 成功 2 跳过）
                results = []
                test_data = testcase.get('test_data', None)
                testcases = []
                if isinstance(test_data, dict):
                    self.process_data(testcase, test_data)
                    testcases.append(testcase)
                elif isinstance(test_data, list):
                    for item in test_data:
                        testcase_copy = copy.deepcopy(testcase)
                        self.process_data(testcase_copy, item)
                        testcases.append(testcase_copy)
                else:
                    testcases.append(testcase)
                for item in testcases:
                    method = item['test_content']['method']
                    path = self.env.env_url + item['test_content']['path']
                    params = item['test_content'].get('params', {})
                    headers = item['test_content'].get('headers', {})
                    data = item['test_content'].get('data', {})
                    # 发送请求
                    response = send_request(method, path, headers, params, data)
                    # 验证期望结果和后置处理
                    post_process = item.get('post_process', {})
                    result = self.validate(response, item['expected_result'], post_process)
                    result['testcase_id'] = testcase_id
                    results.append(result)
                logger.info(f"验证结果: {results}")
                return results
            except Exception as e:
                logger.error(str(e))
                return {'testcase_id': testcase_id, 'execute_status': 0, 'actual_result': {'message': str(e)}}

    def execute_all_testcases(self, testcases):
        app = current_app._get_current_object()
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            with current_app.app_context():
                print(current_app.name)
                futures = []
                for testcase in testcases:
                    future = executor.submit(self.execute_testcase, testcase, app)
                    futures.append(future)
                for future in concurrent.futures.as_completed(futures):
                    try:
                        result = future.result()
                        results.extend(result)
                    except Exception as e:
                        logger.error(e)
        return results

    def validate(self, response, expected_result, post_process):
        validate_type = expected_result.get('validate_type', '')
        expected_status = expected_result.get('expected_status', '')
        expected_headers = expected_result.get('expected_headers', {})
        expected_data = expected_result.get('expected_data', '')
        # 设置变量
        if post_process and post_process.get('set_variable', None):
            self.process_response(response, post_process['set_variable'])
        # 初始化结果数据
        result = {'execute_status': 0, 'actual_result': {'message': ''}}
        # 验证 response status code
        if response.status_code == int(expected_status):
            result['execute_status'] = 1
        else:
            result['actual_result']['message'] += f"响应码不正确: {response.status_code}\n"

        # 验证 header
        actual_headers = dict(response.headers)
        if expected_headers and not all(item in actual_headers.items() for item in expected_headers.items()):
            result['execute_status'] = 0
            result['actual_result']['message'] += f"headers验证不正确: {actual_headers}\n"
        # 验证 response data
        try:
            expected_data = json.loads(expected_data) if expected_data else {}
        except ValueError as e:
            logger.info(f"该字符串不能转成JSON对象, 错误信息:{str(e)}")
        try:
            actual_data = response.json()
        except ValueError as e:
            logger.info(f"该字符串不能转成JSON对象, 错误信息:{str(e)}")
            actual_data = response.text
        validate_response_data(validate_type, expected_data, actual_data, result)
        # check db
        if post_process and post_process.get('check_db', None):
            check_db = post_process.get('check_db')
            if not self.engine:
                result['execute_status'] = 0
                result['actual_result']['message'] += f"db配置缺少\n"
            db_data = execute_query(post_process['check_db'], self.engine)
            if isinstance(db_data, dict) and isinstance(check_db['expected_result'], dict):
                if Counter(check_db['expected_result']) != Counter(db_data):
                    result['execute_status'] = 0
                    result['actual_result']['message'] += "db验证失败\n"
            elif isinstance(db_data, list) and isinstance(check_db['expected_result'], list):
                if check_db['expected_result'] != db_data:
                    result['execute_status'] = 0
                    result['actual_result']['message'] += "db验证失败\n"
            else:
                result['execute_status'] = 0
                result['actual_result']['message'] += "db验证失败\n"
        # check redis
        if post_process and post_process.get('check_redis', None):
            check_redis = post_process.get('check_redis')
            if not self.cache:
                result['execute_status'] = 0
                result['actual_result']['message'] += f"redis配置缺少\n"
            for key, value in check_redis.items():
                if self.cache.get(key) != value:
                    result['execute_status'] = 0
                    result['actual_result']['message'] += f"redis key {key}验证失败\n"
        # exec python
        if post_process and post_process.get('exec_python', None):
            exec_python = post_process.get('exec_python')
            if not self.engine:
                result['execute_status'] = 0
                result['actual_result']['message'] += f"db配置缺少\n"
            if not self.cache:
                result['execute_status'] = 0
                result['actual_result']['message'] += f"redis配置缺少\n"
            execute_python_script(exec_python, self.engine, self.cache, result)
        # 最终结果处理
        if result['actual_result']['message'] == '':
            result['actual_result']['message'] = '执行成功' if result['execute_status'] else '执行失败，错误未知'
        result['actual_result'].update({'actual_headers': actual_headers, 'actual_status': response.status_code,
                                        'actual_data': actual_data})
        return result

    def process_data(self, data, test_data):
        if isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, list):
                    self.process_data(item, test_data)
                elif isinstance(item, dict):
                    self.process_data(item, test_data)
                elif isinstance(item, str):
                    item = self.replace_placeholder(item, test_data)
                    data[index] = item
        elif isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    self.process_data(value, test_data)
                elif isinstance(value, dict):
                    self.process_data(value, test_data)
                elif isinstance(value, str):
                    value = self.replace_placeholder(value, test_data)
                    data[key] = value

    def replace_placeholder(self, value, test_data):
        pattern = r"\${([\w\d_]+)}"
        testsuite_id = self.testsuite.get('testsuite_id', "")
        runner_id = self.runner.get('runner_id', "")
        env_id = self.env.env_id
        user_id = self.user.get('user_id', "")
        placeholders = re.findall(pattern, value)
        for placeholder in placeholders:
            testsuite_redis_key = f"testsuite{testsuite_id}_{placeholder}"
            runner_redis_key = f"runner{runner_id}_{placeholder}"
            env_redis_key = f"env{env_id}_{placeholder}"
            testsuite_redis_value = cache.get(testsuite_redis_key)
            runner_redis_value = cache.get(runner_redis_key)
            env_redis_value = cache.get(env_redis_key)
            replacement = ""
            if test_data.get(placeholder, None):
                replacement = test_data[placeholder]
            elif testsuite_redis_value is not None:
                replacement = testsuite_redis_value
            elif runner_redis_value is not None:
                replacement = runner_redis_value
            elif env_redis_value is not None:
                replacement = env_redis_value
            if value == f"${{{placeholder}}}":
                value = replacement
            else:
                value = value.replace(f"${{{placeholder}}}", str(replacement))
        return value

    def process_response(self, response, fields):
        # TODO add user_id
        testsuite_id = self.testsuite.get('testsuite_id', "")
        runner_id = self.runner.get('runner_id', "")
        env_id = self.env.env_id
        user_id = self.user.get('user_id', "")
        try:
            actual_data = response.json()
            for key, value in fields.items():
                jsonpath_expression = parse(value["field"])
                result = [match.value for match in jsonpath_expression.find(actual_data)]
                if result:
                    redis_key = ""
                    if value['prefix'] == "runner":
                        redis_key = f"{value['prefix']}{runner_id}_{key}"
                    elif value['prefix'] == "testsuite":
                        redis_key = f"{value['prefix']}{testsuite_id}_{key}"
                    elif value['prefix'] == "env_id":
                        redis_key = f"{value['prefix']}{env_id}_{key}"
                    cache.set(redis_key, result[0])
        except ValueError as e:
            logger.info(f"该字符串不能转成JSON对象, 错误信息:{str(e)}")

    def execute_testscenario(self, testscenario):
        pass

    def execute_testsuite(self, flow_testcases, single_testcases):
        try:
            results = []
            execute_status = 1
            for testcase in flow_testcases:
                result = self.execute_testcase(testcase)
                results.extend(result)
            if single_testcases:
                result = self.execute_all_testcases(single_testcases)
                results.extend(result)
            if results:
                execute_status = int(all(item['execute_status'] for item in results))
                TestCase.bulk_update_testcases(results, self.user.get('user_id'))
                Result.create_result(results, self.user.get('user_id'))
            return execute_status, results
        except Exception as e:
            logger.error(e)
            raise

    def execute_runner(self):
        try:
            results = []
            runner_execute_status = 1
            testsuite_ids = json.loads(self.runner.get('testsuites')) if self.runner.get('testsuites') else []
            if not testsuite_ids:
                results = [{"message": "缺少测试用例数据"}]
                runner_execute_status = 2
                return runner_execute_status, results
            total, passed_total, failed_total, skipped_total = 0, 0, 0, 0
            start_time = time.time()
            for testsuite_id in testsuite_ids:
                flow_testcases, single_testcases = TestCaseService.get_testsuite_execute_testcases(testsuite_id)
                testsuite_results = []
                execute_status = 1
                for testcase in flow_testcases:
                    result = self.execute_testcase(testcase)
                    testsuite_results.extend(result)
                if single_testcases:
                    result = self.execute_all_testcases(single_testcases)
                    testsuite_results.extend(result)
                for item in testsuite_results:
                    execute_status = execute_status and item['execute_status']
                    item['testsuite_id'] = testsuite_id
                    total += 1
                    passed_total += 1 if execute_status == 1 else 0
                    failed_total += 1 if execute_status == 0 else 0
                    skipped_total += 1 if execute_status == 2 else 0
                runner_execute_status = runner_execute_status and execute_status
                results.extend(testsuite_results)
            end_time = time.time()
            duration = end_time - start_time
            now = datetime.now()
            date_str = now.strftime('%Y-%m-%d')
            report = {
                'report_name': date_str + self.runner.get('runner_name'),
                'project_id': self.runner.get('project_id'),
                'source': 'Runner',
                'env_id': self.runner.get('env_id'),
                'duration': duration * 1000,
                'total': total,
                'passed_total': passed_total,
                'failed_total': failed_total,
                'skipped_total': skipped_total,
                'creator': self.user.get('user_id'),
                'updater': self.user.get('user_id')
            }
            report_id = Report.create_report(report)
            if results:
                TestCase.bulk_update_testcases(results, self.user.get('user_id'))
                insert_dict = {
                    'report_id': report_id,
                    'runner_id': self.runner.get('runner_id'),
                    'project_id': self.runner.get('project_id'),
                    'creator': self.user.get('user_id'),
                    'updater': self.user.get('user_id')
                }
                Result.create_report_result(insert_dict, results)
            return runner_execute_status, results
        except Exception as e:
            logger.error(e)
            raise

