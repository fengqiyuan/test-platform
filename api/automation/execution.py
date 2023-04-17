#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 11:22
# author: fengqiyuan
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from blueprints import execution_bp
from common.logger import logger
from models.analytics.result import Result
from models.config.environment import Environment
from models.testmgmt.testcase import TestCase
from services.account.role_service import check_permission, check_project_permission
from services.automation.execution_service import ExecutionService
from services.automation.runner_service import RunnerService
from services.testmgmt.testcase_service import TestCaseService


@execution_bp.route('/debug', methods=['POST'])
@jwt_required()
@check_permission('debug_testcase', scope='project')
def debug_testcase():
    try:
        env = Environment.get_environment(request.args.get('env_id', 0, int))
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        testcase = request.json
        if not isinstance(testcase, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        project_id = env.project_id
        if not check_project_permission(user_id, project_id, 'debug_testcase'):
            return jsonify(errcode=1, message="无权限")
        execute = ExecutionService(env)
        response = execute.debug_testcase(testcase)
        return response
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, execute_status=0, message=e), 500


@execution_bp.route('/testcase/<int:testcase_id>', methods=['POST'])
@jwt_required()
@check_permission('execute_testcase', scope='project')
def execute_testcase(testcase_id):
    try:
        env = Environment.get_environment(request.args.get('env_id', 0, int))
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        testcase = TestCaseService.get_execute_testcases(testcase_id)
        if not testcase:
            return jsonify(errcode=1, message='缺少测试用例数据')
        user = get_jwt_identity()
        creator = user.get('user_id')
        if not check_project_permission(creator, testcase.get('project_id'), 'execute_testcase') or \
                not check_project_permission(creator, env.project_id, 'execute_testcase'):
            return jsonify(errcode=1, message="无权限")
        execute = ExecutionService(env)
        results = execute.execute_testcase(testcase)
        execute_status = int(all(item['execute_status'] for item in results))
        TestCase.bulk_update_testcases(results, creator)
        Result.create_result(results, creator)
        if execute_status:
            return jsonify(errcode=0, execute_status=execute_status, results=results)
        else:
            return jsonify(errcode=1, execute_status=execute_status, results=results)
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, execute_status=0, message=e), 500


@execution_bp.route('/scenario/<int:scenario_id>', methods=['POST'])
@jwt_required()
@check_permission('execute_scenario', scope='project')
def execute_scenario(scenario_id):
    try:
        env = Environment.get_environment(request.args.get('env_id', 0, int))
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        testcases = TestCaseService.get_scenario_execute_testcases(scenario_id)
        if not testcases:
            return jsonify(errcode=1, message='缺少测试用例数据')
        user = get_jwt_identity()
        creator = user.get('user_id')
        if not check_project_permission(creator, testcases[0].get('project_id'), 'execute_scenario') or \
                not check_project_permission(creator, env.project_id, 'execute_scenario'):
            return jsonify(errcode=1, message="无权限")
        execute = ExecutionService(env)
        results = execute.execute_all_testcases(testcases)
        execute_status = int(all(item['execute_status'] for item in results))
        TestCase.bulk_update_testcases(results, creator)
        Result.create_result(results, creator)
        if execute_status:
            return jsonify(errcode=0, execute_status=execute_status, results=results)
        else:
            return jsonify(errcode=1, execute_status=execute_status, results=results)
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, execute_status=0, message=e), 500


@execution_bp.route('/testsuite/<int:testsuite_id>', methods=['POST'])
@jwt_required()
@check_permission('execute_testsuite', scope='project')
def execute_testsuite(testsuite_id):
    try:
        env = Environment.get_environment(request.args.get('env_id', 0, int))
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        flow_testcases, single_testcases = TestCaseService.get_testsuite_execute_testcases(testsuite_id)
        testcases = flow_testcases + single_testcases
        if not testcases:
            return jsonify(errcode=1, message='缺少测试用例数据')
        user = get_jwt_identity()
        creator = user.get('user_id')
        if not check_project_permission(creator, testcases[0].get('project_id'), 'execute_testsuite') or \
                not check_project_permission(creator, env.project_id, 'execute_testsuite'):
            return jsonify(errcode=1, message="无权限")
        execute = ExecutionService(env, user=user)
        execute_status, results = execute.execute_testsuite(flow_testcases, single_testcases)
        if execute_status:
            return jsonify(errcode=0, execute_status=execute_status, results=results)
        else:
            return jsonify(errcode=1, execute_status=execute_status, results=results)
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, execute_status=0, message=e), 500


@execution_bp.route('/runner/<int:runner_id>', methods=['POST'])
@jwt_required()
@check_permission('execute_runner', scope='project')
def execute_runner(runner_id):
    try:
        env = Environment.get_environment(request.args.get('env_id', 0, int))
        if not env:
            return jsonify(errcode=1, message='缺少执行环境数据')
        runner = RunnerService.get_execute_runner(runner_id)
        if not runner:
            return jsonify(errcode=1, execute_status=0, message='缺少Runner数据')
        user = get_jwt_identity()
        creator = user.get('user_id')
        if not check_project_permission(creator, runner.get('project_id'), 'execute_runner') or \
                not check_project_permission(creator, env.project_id, 'execute_runner'):
            return jsonify(errcode=1, message="无权限")
        execute = ExecutionService(env, runner=runner, user=user)
        runner_execute_status, results = execute.execute_runner()
        if runner_execute_status:
            return jsonify(errcode=0, execute_status=runner_execute_status, results=results)
        else:
            return jsonify(errcode=1, execute_status=runner_execute_status, results=results)
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, execute_status=0, message=e), 500
