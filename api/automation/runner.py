#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/20 22:05
# author: fengqiyuan
import json
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required

from blueprints import runner_bp
from common.logger import logger
from models.automation.runner import Runner
from models.config.environment import Environment
from services.account.role_service import check_project_permission, check_permission, get_project_role_project_ids
from services.automation.runner_service import RunnerService
from services.testmgmt.testsuite_service import TestSuiteService


@runner_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_runner', scope='project')
def create_runner():
    try:
        runner = request.json
        if not isinstance(runner, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        runner_name = runner.get('runner_name')
        description = runner.get('description')
        project_id = runner.get('project_id')
        env_id = runner.get('env_id')
        testsuites = runner.get('testsuites')
        if not runner_name or not project_id or not env_id or not testsuites:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(runner_name, str) or not isinstance(project_id, int) or not isinstance(env_id, int) or \
                not isinstance(description, (str, type(None))) or not isinstance(testsuites, list):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        creator = user.get('user_id')
        if not check_project_permission(creator, project_id, 'create_runner'):
            return jsonify(errcode=1, message="无权限")
        env = Environment.get_environment(env_id)
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        if not check_project_permission(creator, env.project_id, 'create_runner'):
            return jsonify(errcode=1, message="无权限")
        if not all(isinstance(testsuite.get('testsuite_id'), int) for testsuite in testsuites):
            return jsonify(errcode=1, message='字段类型不正确')
        testsuites_list = []
        testsuite_ids = []
        for testsuite in testsuites:
            testsuite_id = testsuite.get('testsuite_id')
            if not testsuite_id:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(testsuite_id, int):
                return jsonify(errcode=1, message='字段类型不正确')
            testsuites_list.append({'testsuite_id': testsuite_id})
            testsuite_ids.append(testsuite_id)
        if not TestSuiteService.check_testsuite_ids(testsuite_ids):
            return jsonify(errcode=1, message='testsuites数据不正确')
        runner_dict = {
            'runner_name': runner_name,
            'description': description,
            'project_id': project_id,
            'env_id': env_id
        }
        RunnerService.create_runner(runner_dict, testsuites_list, creator)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@runner_bp.route('/<int:runner_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_runner', scope='project')
def update_runner(runner_id):
    try:
        runner = request.json
        if not isinstance(runner, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        runner_name = runner.get('runner_name')
        description = runner.get('description')
        project_id = runner.get('project_id')
        env_id = runner.get('env_id')
        testsuites = runner.get('testsuites')
        user = get_jwt_identity()
        updater = user.get('user_id')
        if not runner_name or not project_id or not env_id or not testsuites:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(runner_name, str) or not isinstance(project_id, int) or not isinstance(env_id, int) or \
                not isinstance(description, (str, type(None))) or not isinstance(testsuites, list):
            return jsonify(errcode=1, message='字段类型不正确')
        if not check_project_permission(updater, project_id, 'create_runner'):
            return jsonify(errcode=1, message="无权限")
        env = Environment.get_environment(env_id)
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        if not check_project_permission(updater, env.project_id, 'update_runner'):
            return jsonify(errcode=1, message="无权限")
        if not all(isinstance(testsuite.get('testsuite_id'), int) for testsuite in testsuites):
            return jsonify(errcode=1, message='字段类型不正确')
        testsuites_list = []
        testsuite_ids = []
        for testsuite in testsuites:
            testsuite_id = testsuite.get('testsuite_id')
            if not testsuite_id:
                return jsonify(errcode=1, message='缺少必填字段')
            if not isinstance(testsuite_id, int):
                return jsonify(errcode=1, message='字段类型不正确')
            testsuites_list.append({'testsuite_id': testsuite_id})
            testsuite_ids.append(testsuite_id)
        if not TestSuiteService.check_testsuite_ids(testsuite_ids):
            return jsonify(errcode=1, message='testsuites数据不正确')
        runner_dict = {
            'runner_name': runner_name,
            'description': description,
            'project_id': project_id,
            'env_id': env_id
        }
        RunnerService.update_runner(runner_id, runner_dict, testsuite_ids, testsuites_list, updater)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@runner_bp.route('/<int:runner_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_runner', scope='project')
def delete_runner(runner_id):
    try:
        user = get_jwt_identity()
        updater = user.get('user_id')
        runner = Runner.get_runner(runner_id)
        if not runner:
            return jsonify(errcode=1, message="无有效数据")
        if not check_project_permission(updater, runner.get('project_id'), 'delete_runner'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {'status': False, 'updater': updater}
        Runner.update_runner(runner_id, update_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        return jsonify(errcode=1, message=str(e)), 500


@runner_bp.route('/<int:runner_id>', methods=['GET'])
@jwt_required()
@check_permission('get_runners', scope='project')
def get_runner(runner_id):
    user = get_jwt_identity()
    updater = user.get('user_id')
    runner = RunnerService.get_runner(runner_id)
    if not runner:
        return jsonify(errcode=1, message="无有效数据")
    if not check_project_permission(updater, runner.get('project_id'), 'get_runners'):
        return jsonify(errcode=1, message="无权限")
    runner['testsuites'] = RunnerService.get_runner_testsuites(runner_id)
    return jsonify(errcode=0, message="查询成功", data=runner)


@runner_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_runners', scope='project')
def get_runners():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_runners')
    runners, total, page_total, iter_pages = RunnerService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, message="查询成功", data=runners, total=total, page_total=page_total,
                   iter_pages=iter_pages)


@runner_bp.route('/search', methods=['GET'])
@jwt_required()
@check_permission('get_runners', scope='project')
def search_runners():
    project_id = request.args.get("project_id", type=int)
    keyword = request.args.get("query")
    if not project_id or not keyword:
        return jsonify(errcode=1, message='缺少必填字段')
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_project_permission(user_id, project_id, 'get_runners'):
        return jsonify(errcode=1, message="无权限")
    data = Runner.search_runners(project_id, keyword)
    return jsonify(errcode=0, data=data)

