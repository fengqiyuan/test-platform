#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/4 11:54
# author: fengqiyuan
from flask import request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import insert, update, select

from common.logger import logger
from exts import db
from models.config.module import Module
from blueprints import module_bp
from services.account.role_service import check_permission, check_project_permission, check_model_permission, \
    get_project_role_project_ids
from services.config.module_service import ModuleService


@module_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_module', scope='project')
def create_module():
    try:
        module = request.json
        if not isinstance(module, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        module_code = module.get('module_code')
        module_name = module.get('module_name')
        description = module.get('description')
        project_id = module.get('project_id')
        if not module_code or not module_name or not project_id:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(module_code, str) or not isinstance(module_name, str) or \
                not isinstance(description, (str, type(None))) or not isinstance(project_id, int):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'create_module'):
            return jsonify(errcode=1, message="无权限")
        insert_dict = {
            'module_code': module_code,
            'module_name': module_name,
            'project_id': project_id,
            'description': description,
            'creator': user_id,
            'updater': user_id
        }
        stmt = insert(Module).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@module_bp.route('/<int:module_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_module', scope='project')
def update_module(module_id):
    try:
        module = request.json
        if not isinstance(module, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        module_code = module.get('module_code')
        module_name = module.get('module_name')
        description = module.get('description')
        project_id = module.get('project_id')
        if not module_code or not module_name or not project_id:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(module_code, str) or not isinstance(module_name, str) or \
                not isinstance(description, (str, type(None))) or not isinstance(project_id, int):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_module'):
            return jsonify(errcode=1, message="无权限")
        update_dict = {
            'module_code': module_code,
            'module_name': module_name,
            'project_id': project_id,
            'description': description,
            'updater': user_id
        }
        stmt = update(Module).where(Module.module_id == module_id, Module.status == True).values(**update_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@module_bp.route('/<int:module_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_module', scope='project')
def delete_module(module_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_model_permission(user_id, Module, module_id, 'delete_module'):
            return jsonify(errcode=1, message="无权限")
        stmt = update(Module).where(Module.module_id == module_id,
                                    Module.status == True).values(status=False, updater=user_id)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@module_bp.route('/<int:module_id>', methods=['GET'])
@jwt_required()
@check_permission('get_modules', scope='project')
def get_module(module_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    module = Module.get_module(module_id)
    if not module:
        return jsonify(errcode=1, message="无有效数据")
    if not check_project_permission(user_id, module.get('project_id'), 'get_modules'):
        return jsonify(errcode=1, message="无权限")
    return jsonify(errcode=0, data=module)


@module_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_modules', scope='project')
def get_modules():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_modules')
    modules, total, page_total, iter_pages = ModuleService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, data=modules, total=total, page_total=page_total, iter_pages=iter_pages)


@module_bp.route('/search', methods=['GET'])
@jwt_required()
@check_permission('get_modules', scope='project')
def search_modules():
    project_id = request.args.get("project_id", type=int)
    keyword = request.args.get("query")
    if not project_id or not keyword:
        return jsonify(errcode=1, message='缺少必填字段')
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_project_permission(user_id, project_id, 'get_modules'):
        return jsonify(errcode=1, message="无权限")
    data = Module.search_modules(project_id, keyword)
    return jsonify(errcode=0, data=data)



