#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/13 17:09
# author: fengqiyuan
import json

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from common.logger import logger
from models.testmgmt.testcase import TestCase
from blueprints import testcase_bp
from models.testmgmt.testscenario import TestScenario
from services.account.role_service import check_permission, check_model_permission, check_project_permission
from services.testmgmt.testcase_service import TestCaseService


@testcase_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_testcase', scope='project')
def create_testcase():
    try:
        testcase = request.json
        if not isinstance(testcase, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        scenario_id = testcase.get('scenario_id')
        project_id = testcase.get('project_id')
        testcase_name = testcase.get('testcase_name')
        test_priority = testcase.get('test_priority')
        test_content = testcase.get('test_content')
        expected_result = testcase.get('expected_result')
        description = testcase.get('description')
        pre_process = testcase.get('pre_process')
        test_data = testcase.get('test_data')
        post_process = testcase.get('post_process')
        testcase_type = 'API平台'
        if not scenario_id or not project_id or not testcase_name or not test_priority or not test_content or \
                not expected_result:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(scenario_id, int) or not isinstance(project_id, int) or \
                not isinstance(testcase_name, str) or not isinstance(test_priority, str) or \
                not isinstance(test_content, dict) or not isinstance(expected_result, dict) or \
                not isinstance(description, (str, type(None))) or not isinstance(pre_process, (dict, type(None))) or \
                not isinstance(test_data, (dict, type(None))) or not isinstance(post_process, (dict, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        if not TestScenario.check_scenario_id(scenario_id):
            return jsonify(errcode=1, message="scenario_id无效")
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'create_testcase'):
            return jsonify(errcode=1, message="无权限")
        if not check_model_permission(user_id, TestScenario, scenario_id, 'create_testcase'):
            return jsonify(errcode=1, message="无权限")
        if testcase_type == 'API平台':
            path = test_content.get('path')
            method = test_content.get('method')
            validate_type = expected_result.get('validate_type')
            expected_status = expected_result.get('expected_status')
            expected_data = expected_result.get('expected_data')
            if not path or not method or not validate_type or not expected_status or not expected_data:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(path, str) or not isinstance(method, str) or \
                    not isinstance(validate_type, str) or not isinstance(expected_status, str) or \
                    not isinstance(expected_data, str):
                return jsonify(errcode=1, message='字段类型不正确')
        elif testcase_type == 'API脚本':
            pass
        elif testcase_type == 'WEB脚本':
            pass
        elif testcase_type == 'APP脚本':
            pass
        insert_dict = {
            'testcase_name': testcase_name,
            'test_type': testcase_type,
            'test_priority': int(test_priority),
            'test_content': test_content,
            'expected_result': expected_result,
            'description': description,
            'scenario_id': scenario_id,
            'project_id': project_id,
            'creator': user_id,
            'updater': user_id
        }
        if pre_process:
            insert_dict.update({'pre_process': pre_process})
        if test_data:
            insert_dict.update({'test_data': test_data})
        if post_process:
            insert_dict.update({'post_process': post_process})
        TestCase.create_testcase(insert_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@testcase_bp.route('/<int:testcase_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_testcase', scope='project')
def update_testcase(testcase_id):
    try:
        testcase = request.json
        if not isinstance(testcase, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        scenario_id = testcase.get('scenario_id')
        project_id = testcase.get('project_id')
        testcase_name = testcase.get('testcase_name')
        test_priority = testcase.get('test_priority')
        test_content = testcase.get('test_content')
        expected_result = testcase.get('expected_result')
        description = testcase.get('description')
        pre_process = testcase.get('pre_process')
        test_data = testcase.get('test_data')
        post_process = testcase.get('post_process')
        testcase_type = 'API平台'
        if not scenario_id or not project_id or not testcase_name or not test_priority or not test_content or \
                not expected_result:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(scenario_id, int) or not isinstance(project_id, int) or \
                not isinstance(testcase_name, str) or not isinstance(test_priority, str) or \
                not isinstance(test_content, dict) or not isinstance(expected_result, dict) or \
                not isinstance(description, (str, type(None))) or not isinstance(pre_process, (dict, type(None))) or \
                not isinstance(test_data, (dict, type(None))) or not isinstance(post_process, (dict, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        if not TestScenario.check_scenario_id(scenario_id):
            return jsonify(errcode=1, message="scenario_id无效")
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'create_testcase'):
            return jsonify(errcode=1, message="无权限")
        if not check_model_permission(user_id, TestScenario, scenario_id, 'create_testcase'):
            return jsonify(errcode=1, message="无权限")
        if testcase_type == 'API平台':
            path = test_content.get('path')
            method = test_content.get('method')
            validate_type = expected_result.get('validate_type')
            expected_status = expected_result.get('expected_status')
            expected_data = expected_result.get('expected_data')
            if not path or not method or not validate_type or not expected_status or not expected_data:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(path, str) or not isinstance(method, str) or \
                    not isinstance(validate_type, str) or not isinstance(expected_status, str) or \
                    not isinstance(expected_data, str):
                return jsonify(errcode=1, message='字段类型不正确')
        elif testcase_type == 'API脚本':
            pass
        elif testcase_type == 'WEB脚本':
            pass
        elif testcase_type == 'APP脚本':
            pass
        update_dict = {
            'testcase_name': testcase_name,
            'test_type': testcase_type,
            'test_priority': int(test_priority),
            'test_content': test_content,
            'expected_result': expected_result,
            'pre_process': pre_process,
            'test_data': test_data,
            'post_process': post_process,
            'description': description,
            'scenario_id': scenario_id,
            'project_id': project_id,
            'updater': user_id
        }
        TestCase.update_testcase(testcase_id, update_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@testcase_bp.route('/<int:testcase_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_testcase', scope='project')
def delete_testcase(testcase_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not TestCase.check_testcase_id(testcase_id):
            return jsonify(errcode=1, message="无有效数据")
        if not check_model_permission(user_id, TestCase, testcase_id, 'delete_testcase'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {'status': False, 'updater': user_id}
        TestCase.update_testcase(testcase_id, update_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message='数据库报错', error=str(e)), 500


@testcase_bp.route('/<int:testcase_id>', methods=['GET'])
@jwt_required()
@check_permission('get_testcases', scope='project')
def get_testcase(testcase_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not TestCase.check_testcase_id(testcase_id):
        return jsonify(errcode=1, message="无有效数据")
    if not check_model_permission(user_id, TestCase, testcase_id, 'get_testcases'):
        return jsonify(errcode=1, message="无权限")
    result = TestCaseService.get_testcase(testcase_id)
    return jsonify(errcode=0, data=result)


@testcase_bp.route('/search', methods=['GET'])
@jwt_required()
@check_permission('get_testcases', scope='project')
def search_project_testcases():
    project_id = request.args.get("project_id", type=int)
    keyword = request.args.get("query")
    if not project_id or not keyword:
        return jsonify(errcode=1, message='缺少必填字段')
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_project_permission(user_id, project_id, 'get_testcases'):
        return jsonify(errcode=1, message="无权限")
    result = TestCaseService.get_project_testcases(project_id, keyword)
    return jsonify(errcode=0, data=result)
