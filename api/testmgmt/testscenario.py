#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:55
# author: fengqiyuan
from dataclasses import asdict

from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from common.logger import logger
from models.config.module import Module
from models.testmgmt.testscenario import TestScenario
from blueprints import scenario_bp
from services.account.role_service import check_permission, check_project_permission, check_model_permission, \
    get_project_role_project_ids
from services.testmgmt.testcase_service import TestCaseService
from services.testmgmt.testscenario_service import TestScenarioService


@scenario_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_scenario', scope='project')
def create_scenario():
    try:
        scenario = request.json
        if not isinstance(scenario, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        scenario_code = scenario.get('scenario_code')
        scenario_name = scenario.get('scenario_name')
        scenario_level = scenario.get('scenario_level')
        scenario_type = scenario.get('scenario_type')
        project_id = scenario.get('project_id')
        module_id = scenario.get('module_id')
        description = scenario.get('description')
        if not scenario_code or not scenario_name or not scenario_level or not scenario_type or \
                not project_id or not module_id:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(scenario_code, str) or not isinstance(scenario_name, str) or \
                not isinstance(scenario_level, str) or not isinstance(scenario_type, str) or \
                not isinstance(project_id, int) or not isinstance(module_id, int) or \
                not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'create_scenario'):
            return jsonify(errcode=1, message="无权限")
        if not Module.check_module(module_id, project_id):
            return jsonify(errcode=1, message="模块和项目不匹配")
        insert_dict = {
            'scenario_code': scenario_code,
            'scenario_name': scenario_name,
            'scenario_level': scenario_level,
            'scenario_type': scenario_type,
            'project_id': project_id,
            'module_id': module_id,
            'description': description,
            'creator': user_id,
            'updater': user_id
        }
        TestScenario.create_scenario(insert_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        return jsonify(errcode=1, message=str(e)), 500


@scenario_bp.route('/<int:scenario_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_scenario', scope='project')
def update_scenario(scenario_id):
    try:
        scenario = request.json
        if not isinstance(scenario, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        scenario_code = scenario.get('scenario_code')
        scenario_name = scenario.get('scenario_name')
        scenario_level = scenario.get('scenario_level')
        scenario_type = scenario.get('scenario_type')
        project_id = scenario.get('project_id')
        module_id = scenario.get('module_id')
        description = scenario.get('description')
        if not scenario_code or not scenario_name or not scenario_level or not scenario_type or \
                not project_id or not module_id:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(scenario_code, str) or not isinstance(scenario_name, str) or \
                not isinstance(scenario_level, int) or not isinstance(scenario_type, str) or \
                not isinstance(project_id, int) or not isinstance(module_id, int) or \
                not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_scenario'):
            return jsonify(errcode=1, message="无权限")
        if not Module.check_module(module_id, project_id):
            return jsonify(errcode=1, message="模块和项目不匹配")
        update_dict = {
            'scenario_code': scenario_code,
            'scenario_name': scenario_name,
            'scenario_level': scenario_level,
            'scenario_type': scenario_type,
            'project_id': project_id,
            'module_id': module_id,
            'description': description,
            'updater': user_id
        }
        TestScenario.update_scenario(scenario_id, update_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        return jsonify(errcode=1, message=str(e)), 500


@scenario_bp.route('/<int:scenario_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_scenario', scope='project')
def delete_scenario(scenario_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not TestScenario.check_scenario_id(scenario_id):
            return jsonify(errcode=1, message="无有效数据")
        if not check_model_permission(user_id, TestScenario, scenario_id, 'delete_scenario'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {
            'status': False,
            'updater': user_id
        }
        TestScenario.update_scenario(scenario_id, update_dict)
        return jsonify(errcode=0, message="删除成功")
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@scenario_bp.route('/import', methods=['PUT'])
@jwt_required()
@check_permission('import_scenario', scope='project')
def import_scenario():
    pass


@scenario_bp.route('/importWithGit', methods=['POST'])
@jwt_required()
@check_permission('create_scenario_with_git', scope='project')
def create_scenario_with_git():
    pass


@scenario_bp.route('/importWithExcel', methods=['POST'])
@jwt_required()
@check_permission('create_scenario_with_excel', scope='project')
def create_scenario_with_excel():
    pass


@scenario_bp.route('/<int:scenario_id>', methods=['GET'])
@jwt_required()
@check_permission('get_scenarios', scope='project')
def get_scenario(scenario_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not TestScenario.check_scenario_id(scenario_id):
        return jsonify(errcode=1, message="无有效数据")
    if not check_model_permission(user_id, TestScenario, scenario_id, 'get_scenarios'):
        return jsonify(errcode=1, message="无权限")
    testscenario = TestScenarioService.get_scenario(scenario_id)
    return jsonify(errcode=0, message="查询成功", data=testscenario)


@scenario_bp.route('/<int:scenario_id>/testcases', methods=['GET'])
@jwt_required()
@check_permission('get_scenarios', scope='project')
def get_scenario_testcases(scenario_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not TestScenario.check_scenario_id(scenario_id):
        return jsonify(errcode=1, message="无有效数据")
    if not check_model_permission(user_id, TestScenario, scenario_id, 'get_scenarios'):
        return jsonify(errcode=1, message="无权限")
    testcases = TestCaseService.get_scenario_testcases(scenario_id)
    return jsonify(errcode=0, message="查询成功", data=testcases)


@scenario_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_scenarios', scope='project')
def get_scenarios():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_scenarios')
    testscenarios, total, page_total, iter_pages = TestScenarioService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, data=testscenarios, total=total, page_total=page_total, iter_pages=iter_pages)
