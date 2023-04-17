#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/13 17:09
# author: fengqiyuan
import json

from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from common.logger import logger
from models.testmgmt.testcase import TestCase
from blueprints import testsuite_bp
from models.testmgmt.testsuite import TestSuite, TestSuiteDetail
from services.account.role_service import check_permission, check_model_permission, check_project_permission, \
    get_project_role_project_ids
from services.testmgmt.testsuite_service import TestSuiteService


@testsuite_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_testsuite', scope='project')
def create_testsuite():
    try:
        testsuite = request.json
        if not isinstance(testsuite, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        testsuite_name = testsuite.get('testsuite_name')
        project_id = testsuite.get('project_id')
        sorted_testcases = testsuite.get('sorted_testcases')
        unsorted_testcases = testsuite.get('unsorted_testcases')
        description = testsuite.get('description')
        if not testsuite_name or not project_id or (not sorted_testcases and not unsorted_testcases):
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(testsuite_name, str) or not isinstance(project_id, int) or \
                not isinstance(sorted_testcases, (list, type(None))) or \
                not isinstance(unsorted_testcases, (list, type(None))) or \
                not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'create_testsuite'):
            return jsonify(errcode=1, message="无权限")
        total = len(sorted_testcases) + len(unsorted_testcases)
        single_total = len(unsorted_testcases)
        insert_list = []
        for testcase in sorted_testcases:
            testcase_id = testcase.get('testcase_id')
            order = testcase.get('order')
            if not testcase_id or not order:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(testcase_id, int) or not isinstance(order, int):
                return jsonify(errcode=1, message='字段类型不正确')
            if not check_model_permission(user_id, TestCase, testcase_id, 'create_testsuite'):
                return jsonify(errcode=1, message="无权限")
            insert_list.append({'testcase_id': testcase_id, 'execute_type': True, 'order': order})
        for testcase in unsorted_testcases:
            testcase_id = testcase.get('testcase_id')
            if not testcase_id:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(testcase_id, int):
                return jsonify(errcode=1, message='字段类型不正确')
            if not check_model_permission(user_id, TestCase, testcase_id, 'create_testsuite'):
                return jsonify(errcode=1, message="无权限")
            insert_list.append({'testcase_id': testcase_id, 'execute_type': False, 'order': 0})
        insert_dict = {
            'testsuite_name': testsuite_name,
            'project_id': project_id,
            'total': total,
            'single_total': single_total,
            'description': description
        }
        TestSuiteService.create_testsuite(insert_dict, insert_list, user_id)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@testsuite_bp.route('/<int:testsuite_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_testsuite', scope='project')
def update_testsuite(testsuite_id):
    try:
        testsuite = request.json
        if not isinstance(testsuite, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        testsuite_name = testsuite.get('testsuite_name')
        project_id = testsuite.get('project_id')
        sorted_testcases = testsuite.get('sorted_testcases')
        unsorted_testcases = testsuite.get('unsorted_testcases')
        description = testsuite.get('description')
        if not testsuite_name or not project_id or (not sorted_testcases and not unsorted_testcases):
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(testsuite_name, str) or not isinstance(project_id, int) or \
                not isinstance(sorted_testcases, (list, type(None))) or \
                not isinstance(unsorted_testcases, (list, type(None))) or \
                not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_testsuite'):
            return jsonify(errcode=1, message="无权限")
        total = len(sorted_testcases) + len(unsorted_testcases)
        single_total = len(unsorted_testcases)
        update_list = []
        for testcase in sorted_testcases:
            testcase_id = testcase.get('testcase_id')
            order = testcase.get('order')
            if not testcase_id or not order:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(testcase_id, int) or not isinstance(order, int):
                return jsonify(errcode=1, message='字段类型不正确')
            if not check_model_permission(user_id, TestCase, testcase_id, 'update_testsuite'):
                return jsonify(errcode=1, message="无权限")
            update_list.append({'testcase_id': testcase_id, 'execute_type': True, 'order': order})
        for testcase in unsorted_testcases:
            testcase_id = testcase.get('testcase_id')
            if not testcase_id:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(testcase_id, int):
                return jsonify(errcode=1, message='字段类型不正确')
            if not check_model_permission(user_id, TestCase, testcase_id, 'update_testsuite'):
                return jsonify(errcode=1, message="无权限")
            update_list.append({'testcase_id': testcase_id, 'execute_type': False, 'order': 0})
        update_dict = {
            'testsuite_name': testsuite_name,
            'project_id': project_id,
            'total': total,
            'single_total': single_total,
            'description': description
        }
        TestSuiteService.update_testsuite(testsuite_id, update_dict, update_list, user_id)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@testsuite_bp.route('/<int:testsuite_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_testsuite', scope='project')
def delete_testsuite(testsuite_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not TestSuiteService.check_testsuite_id(testsuite_id):
            return jsonify(errcode=1, message="无有效数据")
        if not check_model_permission(user_id, TestSuite, testsuite_id, 'delete_testsuite'):
            return jsonify(errcode=1, message="无权限")
        TestSuiteService.delete_testsuite(testsuite_id, user_id)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@testsuite_bp.route('/<int:testsuite_id>', methods=['GET'])
@jwt_required()
@check_permission('get_testsuites', scope='project')
def get_testsuite(testsuite_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not TestSuiteService.check_testsuite_id(testsuite_id):
        return jsonify(errcode=1, message="无有效数据")
    if not check_model_permission(user_id, TestSuite, testsuite_id, 'get_testsuites'):
        return jsonify(errcode=1, message="无权限")
    result = TestSuiteService.get_testsuite(testsuite_id)
    return jsonify(errcode=0, data=result)


@testsuite_bp.route('/<int:testsuite_id>/testcases', methods=['GET'])
@jwt_required()
@check_permission('get_testsuites', scope='project')
def get_testsuite_detail(testsuite_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not TestSuiteService.check_testsuite_id(testsuite_id):
        return jsonify(errcode=1, message="无有效数据")
    if not check_model_permission(user_id, TestSuite, testsuite_id, 'get_testsuites'):
        return jsonify(errcode=1, message="无权限")
    testsuite = TestSuiteService.get_testsuite(testsuite_id)
    testsuite_detail = TestSuiteService.get_testsuite_detail(testsuite_id)
    return jsonify(errcode=0, testsuite=testsuite, testsuite_detail=testsuite_detail)


@testsuite_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_testsuites', scope='project')
def get_testsuites():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_testsuites')
    testsuites, total, page_total, iter_pages = TestSuiteService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, data=testsuites, total=total, page_total=page_total, iter_pages=iter_pages)


@testsuite_bp.route('/search', methods=['GET'])
@jwt_required()
@check_permission('get_testsuites', scope='project')
def get_project_testsuites():
    project_id = request.args.get("project_id", type=int)
    keyword = request.args.get("query")
    if not project_id or not keyword:
        return jsonify(errcode=1, message='缺少必填字段')
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_project_permission(user_id, project_id, 'get_testsuites'):
        return jsonify(errcode=1, message="无权限")
    result = TestSuiteService.get_project_testsuites(project_id, keyword)
    return jsonify(errcode=0, data=result)
