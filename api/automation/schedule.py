#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/20 22:06
# author: fengqiyuan
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from blueprints import schedule_bp
from common.logger import logger
from models.automation.runner import Runner
from models.automation.schedule import Schedule
from services.account.role_service import check_permission, check_project_permission, check_model_permission, \
    get_project_role_project_ids
from services.automation.schedule_service import ScheduleService


@schedule_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_schedule', scope='project')
def create_schedule():
    try:
        schedule = request.json
        if not isinstance(schedule, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        schedule_name = schedule.get('schedule_name')
        project_id = schedule.get('project_id')
        runner_id = schedule.get('runner_id')
        cron = schedule.get('cron')
        description = schedule.get('description')
        if not schedule_name or not project_id or not runner_id or not cron:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(schedule_name, str) or not isinstance(project_id, int) or not isinstance(runner_id, int) or \
                not isinstance(cron, str) or not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        creator = user.get('user_id')
        if not check_project_permission(creator, project_id, 'create_schedule'):
            return jsonify(errcode=1, message="无权限")
        if not check_model_permission(creator, Runner, runner_id, 'create_schedule'):
            return jsonify(errcode=1, message="无权限")
        insert_dict = {
            'schedule_name': schedule_name,
            'project_id': project_id,
            'runner_id': runner_id,
            'cron': cron,
            'description': description,
            'creator': creator,
            'updater': creator
        }
        Schedule.create_schedule(insert_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@schedule_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_schedule', scope='project')
def update_schedule(schedule_id):
    try:
        schedule = request.json
        if not isinstance(schedule, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        schedule_name = schedule.get('schedule_name')
        project_id = schedule.get('project_id')
        runner_id = schedule.get('runner_id')
        cron = schedule.get('cron')
        description = schedule.get('description')
        if not schedule_name or not project_id or not runner_id or not cron:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(schedule_name, str) or not isinstance(project_id, int) or not isinstance(runner_id, int) or \
                not isinstance(cron, str) or not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_schedule'):
            return jsonify(errcode=1, message="无权限")
        if not check_model_permission(user_id, Runner, runner_id, 'update_schedule'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {
            'schedule_name': schedule_name,
            'project_id': project_id,
            'runner_id': runner_id,
            'cron': cron,
            'description': description,
            'updater': user_id
        }
        Schedule.update_schedule(schedule_id, update_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@schedule_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_schedule', scope='project')
def delete_schedule(schedule_id):
    try:
        user = get_jwt_identity()
        updater = user.get('user_id')
        if not check_model_permission(updater, Schedule, schedule_id, 'delete_schedule'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {
            'status': False,
            'updater': updater
        }
        Schedule.update_schedule(schedule_id, update_dict)
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@schedule_bp.route('/<int:schedule_id>', methods=['GET'])
@jwt_required()
@check_permission('get_schedules', scope='project')
def get_schedule(schedule_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_model_permission(user_id, Schedule, schedule_id, 'delete_schedule'):
        return jsonify(errcode=1, message="无权限")
    result = ScheduleService.get_schedule(schedule_id)
    return jsonify(errcode=0, message="查询成功", data=result)


@schedule_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_schedules', scope='project')
def get_schedules():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_schedules')
    schedules, total, page_total, iter_pages = ScheduleService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, message="查询成功", data=schedules, total=total, page_total=page_total,
                   iter_pages=iter_pages)

