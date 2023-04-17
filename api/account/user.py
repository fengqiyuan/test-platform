#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/5 09:58
# author: fengqiyuan
from datetime import datetime

from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import select, insert, update, func

from common.logger import logger
from common.validate import is_valid_datetime
from exts import db
from models.account.role import Role, Permission, RolePermission
from models.account.user import User
from blueprints import user_bp
from models.account.user_role import UserRole, UserProjectRole
from models.config.project import Project
from services.account.role_service import check_permission


@user_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_user')
def create_user():
    try:
        user: dict = request.json
        if not isinstance(user, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        username = user.get('username')
        password = user.get('password')
        email = user.get('email')
        join_time = user.get('join_time', datetime.now())
        avatar = user.get('avatar')
        if not username or not password or not email:
            return jsonify(errcode=1, message='缺少必填项')
        if not isinstance(username, str) or not isinstance(password, str) or not isinstance(email, str) or \
                not isinstance(join_time, (str, datetime)) or not isinstance(avatar, (str, type(None))):
            return jsonify(errcode=1, message='数据类型不正确')
        if isinstance(join_time, str) and not is_valid_datetime(join_time):
            return jsonify(errcode=1, message='join_time格式不正确')
        password_hash, salt = User.generate_password_hash(user['password'])
        operate_user = get_jwt_identity()
        insert_dict = {
            'username': user['username'],
            'password_hash': password_hash,
            'salt': salt,
            'email': user['email'],
            'join_time': user['join_time'],
            'avatar': user['avatar'],
            'creator': operate_user['user_id'],
            'updater': operate_user['user_id']
        }
        stmt = insert(User).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_user')
def update_user(user_id):
    try:
        user: dict = request.json
        if not isinstance(user, dict):
            return jsonify(errcode=1, message='缺少必填项')
        username = user.get('username')
        password = user.get('password')
        email = user.get('email')
        join_time = user.get('join_time')
        avatar = user.get('avatar')
        status = user.get('status')
        if not isinstance(username, (str, type(None))) or not isinstance(password, (str, type(None))) or \
                not isinstance(email, (str, type(None))) or not isinstance(join_time, (str, datetime, type(None))) or \
                not isinstance(avatar, (str, type(None))) or not isinstance(status, (bool, type(None))):
            return jsonify(errcode=1, message='数据类型不正确')
        operate_user = get_jwt_identity()
        update_dict = {'updater': operate_user['user_id']}
        if username:
            update_dict['username'] = username
        if password:
            password_hash, salt = User.generate_password_hash(user['password'])
            update_dict.update({'password_hash': password_hash, 'salt': salt})
        if email:
            update_dict['email'] = email
        if isinstance(join_time, str) and not is_valid_datetime(join_time):
            return jsonify(errcode=1, message='join_time格式不正确')
        if join_time:
            update_dict['join_time'] = join_time
        if avatar:
            update_dict['avatar'] = avatar
        if status:
            update_dict['status'] = status
        if len(update_dict.keys()) == 1:
            return jsonify(errcode=1, message='无更新字段')
        stmt = update(User).where(User.user_id == user_id, User.status == True).values(**update_dict)
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount:
            return jsonify(errcode=0, message='success')
        else:
            return jsonify(errcode=1, message='无有效数据')
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@check_permission('get_user')
def get_user(user_id):
    result = db.session.execute(select(User.user_id, User.username, User.email, User.avatar
                                       ).where(User.user_id == user_id, User.status == True)).first()
    return jsonify(errcode=0, data=result._asdict())


@user_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_users')
def get_users():
    page_no = request.args.get("pageNo", 1, type=int)
    page_size = current_app.config['PER_PAGE_COUNT']
    users, total, page_total, iter_pages = User.paginate(page_no, page_size)
    return jsonify(errcode=0, data=users, total=total, page_total=page_total, iter_pages=iter_pages)


@user_bp.route('/<int:user_id>/roles', methods=['POST'])
@jwt_required()
@check_permission('create_user_role')
def create_user_role(user_id):
    try:
        role_id = request.args.get('role_id', type=int)
        if not role_id:
            return jsonify(errcode=1, message='缺少必填项或数据类型不正确')
        current_role_id = db.session.execute(
            select(UserRole.role_id).where(UserRole.user_id == user_id,
                                           UserRole.role_id == role_id,
                                           UserRole.status == True)).scalar()
        if current_role_id:
            return jsonify(errcode=0, message='角色已存在')
        user = get_jwt_identity()
        insert_dict = {
            'user_id': user_id,
            'role_id': role_id,
            'creator': user.get('user_id'),
            'updater': user.get('user_id')
        }
        stmt = insert(UserRole).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@user_bp.route('/<int:user_id>/roles', methods=['DELETE'])
@jwt_required()
@check_permission('delete_user_role')
def delete_user_role(user_id):
    try:
        role_id = request.args.get('role_id', type=int)
        if not role_id:
            return jsonify(errcode=1, message='缺少必填项或数据类型不正确')
        current_user_id = db.session.execute(
            select(UserRole.user_id).where(UserRole.role_id == role_id,
                                           UserRole.status == True)).scalar()
        if not current_user_id:
            return jsonify(errcode=0, message='用户该角色不存在或已无效')
        user = get_jwt_identity()
        stmt = update(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id, UserRole.status == True
                                      ).values(status=False, updater=user.get('user_id'))
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@user_bp.route('/<int:user_id>/roles', methods=['GET'])
@jwt_required()
@check_permission('get_user_roles')
def get_user_roles(user_id):
    query = select(Role.role_id, Role.role_code, Role.role_name, Permission.permission_code,
                   Permission.permission_name
                   ).join_from(UserRole, Role, UserRole.role_id == Role.role_id) \
        .join(RolePermission, Role.role_id == RolePermission.role_id) \
        .join(Permission, RolePermission.permission_id == Permission.permission_id) \
        .where(UserRole.user_id == user_id, UserRole.status == True, RolePermission.status == True)
    results = db.session.execute(query).all()
    user_role_permissions = []
    for result in results:
        user_role_permissions.append(result._asdict())
    return jsonify(errcode=0, data=user_role_permissions)


@user_bp.route('/<int:user_id>/project-roles', methods=['POST'])
@jwt_required()
@check_permission('create_user_project_role')
def create_user_project_role(user_id):
    try:
        project_id = request.args.get('project_id', type=int)
        role_id = request.args.get('role_id', type=int)
        if not project_id or not role_id:
            return jsonify(errcode=1, message='缺少必填项或数据类型不正确')
        current_role_id = db.session.execute(
            select(UserProjectRole.role_id).where(UserProjectRole.user_id == user_id,
                                                  UserProjectRole.project_id == project_id,
                                                  UserProjectRole.role_id == role_id,
                                                  UserProjectRole.status == True)).scalar()
        if current_role_id:
            return jsonify(errcode=0, message='用户这个项目该角色已存在')
        user = get_jwt_identity()
        insert_dict = {
            'user_id': user_id,
            'project_id': project_id,
            'role_id': role_id,
            'creator': user.get('user_id'),
            'updater': user.get('user_id')
        }
        stmt = insert(UserProjectRole).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@user_bp.route('/<int:user_id>/project-roles', methods=['DELETE'])
@jwt_required()
@check_permission('delete_user_project_role')
def delete_user_project_role(user_id):
    try:
        project_id = request.args.get('project_id', type=int)
        role_id = request.args.get('role_id', type=int)
        if not project_id or not role_id:
            return jsonify(errcode=1, message='缺少必填项或数据类型不正确')
        current_role_id = db.session.execute(
            select(UserProjectRole.role_id).where(UserProjectRole.user_id == user_id,
                                                  UserProjectRole.project_id == project_id,
                                                  UserProjectRole.role_id == role_id,
                                                  UserProjectRole.status == True)).scalar()
        if not current_role_id:
            return jsonify(errcode=0, message='用户这个项目该角色不存在或已无效')
        user = get_jwt_identity()
        stmt = update(UserProjectRole).where(UserProjectRole.user_id == user_id,
                                             UserProjectRole.project_id == project_id,
                                             UserProjectRole.role_id == role_id,
                                             UserProjectRole.status == True
                                             ).values(status=False, updater=user.get('user_id'))
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e))


@user_bp.route('/<int:user_id>/project-roles', methods=['GET'])
@jwt_required()
@check_permission('get_user_project_roles')
def get_user_project_roles(user_id):
    query = select(Project.project_id, Project.project_code, Project.project_name, Role.role_id, Role.role_code,
                   Role.role_name, Permission.permission_code, Permission.permission_name
                   ).join_from(UserProjectRole, Role, UserProjectRole.role_id == Role.role_id) \
        .join(RolePermission, Role.role_id == RolePermission.role_id) \
        .join(Permission, RolePermission.permission_id == Permission.permission_id) \
        .join(Project, UserProjectRole.project_id == Project.project_id) \
        .where(UserProjectRole.user_id == user_id, UserProjectRole.status == True, RolePermission.status == True)
    results = db.session.execute(query).all()
    user_project_role_permissions = []
    for result in results:
        user_project_role_permissions.append(result._asdict())
    return jsonify(errcode=0, data=user_project_role_permissions)
