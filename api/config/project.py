#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/2 15:43
# author: fengqiyuan
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import insert, update

from common.logger import logger
from models.config.project import Project, db
from blueprints import project_bp
from services.account.role_service import check_permission, check_project_permission, get_project_role_project_ids
from services.config.project_service import ProjectService


@project_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_project')
def create_project():
    try:
        project = request.json
        if not isinstance(project, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        project_code = project.get('project_code')
        project_name = project.get('project_name')
        git_url = project.get('git_url')
        description = project.get('description')
        if not project_code or not project_name or not git_url:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(project_code, str) or not isinstance(project_name, str) or \
                not isinstance(git_url, str) or not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        insert_dict = {
            'project_code': project_code,
            'project_name': project_name,
            'git_url': git_url,
            'description': description,
            'creator': user_id,
            'updater': user_id
        }
        stmt = insert(Project).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@project_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_project', scope='project')
def update_project(project_id):
    try:
        project = request.json
        if not isinstance(project, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        project_code = project.get('project_code')
        project_name = project.get('project_name')
        git_url = project.get('git_url')
        description = project.get('description')
        if not project_code or not project_name or not git_url:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(project_code, str) or not isinstance(project_name, str) or \
                not isinstance(git_url, str) or not isinstance(description, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_project'):
            return jsonify(errcode=1, message='无权限')
        update_dict = {
            'project_code': project_code,
            'project_name': project_name,
            'git_url': git_url,
            'description': description,
            'updater': user_id
        }
        stmt = update(Project).where(Project.project_id == project_id, Project.status == True).values(**update_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@project_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_project', scope='project')
def delete_project(project_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_project_permission(user_id, project_id, 'update_project'):
            return jsonify(errcode=1, message='无权限')
        update_dict = {
            'status': False,
            'updater': user_id
        }
        stmt = update(Project).where(Project.project_id == project_id, Project.status == True).values(**update_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@project_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
@check_permission('get_projects', scope='project')
def get_project(project_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project = Project.get_project(project_id)
    if not project:
        return jsonify(errcode=1, message="无有效数据")
    if not check_project_permission(user_id, project_id, 'get_projects'):
        return jsonify(errcode=1, message="无权限")
    return jsonify(errcode=0, data=project)


@project_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_projects', scope='project')
def get_projects():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_projects')
    projects, total, page_total, iter_pages = ProjectService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, data=projects, total=total, page_total=page_total, iter_pages=iter_pages)


@project_bp.route('/search', methods=['GET'])
@jwt_required()
@check_permission('get_projects', scope='project')
def search_projects():
    query = request.args.get("query")
    if not query:
        return jsonify(errcode=1, message='缺少必填字段')
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_projects')
    data = Project.search_project(query, project_ids)
    return jsonify(errcode=0, data=data)


