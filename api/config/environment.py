#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/15 08:27
# author: fengqiyuan
import json

from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import insert, update, select, text

from common.logger import logger
from exts import db
from models.config.environment import Environment
from blueprints import env_bp
from services.account.role_service import check_permission, check_project_permission, check_model_permission, \
    get_project_role_project_ids
from services.config.environment_service import EnvironmentService


@env_bp.route("", methods=['POST'])
@jwt_required()
@check_permission('create_environment', scope='project')
def create_environment():
    try:
        env = request.json
        if not isinstance(env, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        env_name = env.get('env_name')
        protocol = env.get('protocol')
        hostname = env.get('hostname')
        port = env.get('port')
        env_url = env.get('env_url')
        description = env.get('description')
        project_id = env.get('project_id')
        db_config = env.get('db_config')
        redis_config = env.get('redis_config')
        if not env_name or not protocol or not hostname or not port or not env_url or not project_id:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(env_name, str) or not isinstance(protocol, str) or not isinstance(hostname, str) or \
                not isinstance(port, int) or not isinstance(env_url, str) or \
                not isinstance(description, (str, type(None))) or not isinstance(project_id, int) or \
                not isinstance(db_config, (str, dict, type(None))) or \
                not isinstance(redis_config, (str, dict, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'create_environment'):
            return jsonify(errcode=1, message="无权限")
        insert_dict = {
            'env_name': env_name,
            'protocol': protocol,
            'hostname': hostname,
            'port': port,
            'env_url': env_url,
            'description': description,
            'project_id': project_id,
            'creator': user_id,
            'updater': user_id
        }
        if db_config and isinstance(db_config, str):
            insert_dict['db_config'] = json.loads(db_config)
        elif db_config and isinstance(db_config, dict):
            insert_dict['db_config'] = db_config
        if redis_config and isinstance(redis_config, str):
            insert_dict['redis_config'] = json.loads(redis_config)
        elif redis_config and isinstance(redis_config, dict):
            insert_dict['redis_config'] = redis_config
        stmt = insert(Environment).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return jsonify(errcode=1, message=str(e))


@env_bp.route("/<int:env_id>", methods=['PUT'])
@jwt_required()
@check_permission('update_environment', scope='project')
def update_environment(env_id):
    try:
        env = request.json
        if not isinstance(env, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        env_name = env.get('env_name')
        protocol = env.get('protocol')
        hostname = env.get('hostname')
        port = env.get('port')
        env_url = env.get('env_url')
        description = env.get('description')
        project_id = env.get('project_id')
        db_config = env.get('db_config')
        redis_config = env.get('redis_config')
        if not env_name or not protocol or not hostname or not port or not env_url or not project_id:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(env_name, str) or not isinstance(protocol, str) or not isinstance(hostname, str) or \
                not isinstance(port, int) or not isinstance(env_url, str) or \
                not isinstance(description, (str, type(None))) or not isinstance(project_id, int) or \
                not isinstance(db_config, (str, dict, type(None))) or \
                not isinstance(redis_config, (str, dict, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_environment'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {
            'env_name': env_name,
            'protocol': protocol,
            'hostname': hostname,
            'port': port,
            'env_url': env_url,
            'description': description,
            'project_id': project_id,
            'updater': user_id
        }
        if db_config and isinstance(db_config, str):
            update_dict['db_config'] = json.loads(db_config)
        elif db_config and isinstance(db_config, (dict, type(None))):
            update_dict['db_config'] = db_config
        if redis_config and isinstance(redis_config, str):
            update_dict['redis_config'] = json.loads(redis_config)
        elif redis_config and isinstance(redis_config, (dict, type(None))):
            update_dict['redis_config'] = redis_config
        stmt = update(Environment).where(Environment.env_id == env_id).values(**update_dict)
        db.session.execute(stmt)
        if not db_config:
            db.session.execute(text(f'UPDATE environment SET db_config=NULL WHERE env_id = {env_id}'))
        if not redis_config:
            db.session.execute(text(f'UPDATE environment SET redis_config=NULL WHERE env_id = {env_id}'))
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return jsonify(errcode=1, message=str(e))


@env_bp.route("/<int:env_id>", methods=['DELETE'])
@jwt_required()
@check_permission('delete_environment', scope='project')
def delete_environment(env_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_model_permission(user_id, Environment, env_id, 'delete_environment'):
            return jsonify(errcode=1, message="无权限")
        db.session.execute(
            update(Environment).where(Environment.env_id == env_id, Environment.status == True
                                      ).values(status=False, updater=user_id)
        )
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        return jsonify(errcode=1, message=str(e))


@env_bp.route("/<int:env_id>", methods=['GET'])
@jwt_required()
@check_permission('get_environments', scope='project')
def get_environment(env_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    env = Environment.get_environment_dict(env_id)
    if not env:
        return jsonify(errcode=1, message="无有效数据")
    if not check_project_permission(user_id, env.get('project_id'), 'get_environments'):
        return jsonify(errcode=1, message="无权限")
    return jsonify(errcode=0, message='success', data=env)


@env_bp.route("", methods=['GET'])
@jwt_required()
@check_permission('get_environments', scope='project')
def get_environments():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_environments')
    envs, total, page_total, iter_pages = EnvironmentService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, data=envs, total=total, page_total=page_total, iter_pages=iter_pages)


@env_bp.route('/search', methods=['GET'])
@jwt_required()
@check_permission('get_environments', scope='project')
def search_environments():
    project_id = request.args.get("project_id")
    keyword = request.args.get("query")
    if not project_id or not keyword:
        return jsonify(errcode=1, message='缺少必填字段')
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_project_permission(user_id, project_id, 'get_environments'):
        return jsonify(errcode=1, message="无权限")
    data = Environment.search_environment(project_id, keyword)
    return jsonify(errcode=0, data=data)
