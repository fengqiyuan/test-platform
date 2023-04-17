#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/4/9 11:35
# author: fengqiyuan
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, insert, update, select
from blueprints import role_bp
from common.logger import logger
from models.account.role import Role, db, Permission, RolePermission
from services.account.role_service import check_permission


@role_bp.route('', methods=['POST'])
@jwt_required()
@check_permission('create_role')
def create_role():
    try:
        role = request.json
        if not isinstance(role, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        role_code = role.get('role_code')
        role_name = role.get('role_name')
        if not role_code or not role_name:
            return jsonify(errcode=1, message='缺少必填项')
        if not isinstance(role_code, str) or not isinstance(role_name, str):
            return jsonify(errcode=1, message='数据类型不正确')
        role_id = db.session.execute(
            select(Role.role_id).where(Role.role_code == role_code, Role.status == True)).scalar()
        if role_id:
            return jsonify(errcode=1, message='角色role_code已存在')
        user = get_jwt_identity()
        insert_dict = {
            'role_code': role_code,
            'role_name': role_name,
            'creator': user.get('user_id'),
            'updater': user.get('user_id')
        }
        stmt = insert(Role).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/<int:role_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_role')
def update_role(role_id):
    try:
        role = request.json
        if not isinstance(role, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        role_code = role.get('role_code')
        role_name = role.get('role_name')
        if not role_code or not role_name:
            return jsonify(errcode=1, message='缺少必填项')
        if not isinstance(role_code, str) or not isinstance(role_name, str):
            return jsonify(errcode=1, message='数据类型不正确')
        current_role_id = db.session.execute(
            select(Role.role_id).where(Role.role_code == role_code, Role.status == True)).scalar()
        if current_role_id and current_role_id != role_id:
            return jsonify(errcode=1, message='角色role_code已存在')
        user = get_jwt_identity()
        update_dict = {
            'role_code': role_code,
            'role_name': role_name,
            'updater': user.get('user_id')
        }
        stmt = update(Role).where(Role.role_id == role_id, Role.status == True).values(**update_dict)
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount:
            return jsonify(errcode=0, message='success')
        else:
            return jsonify(errcode=1, message='无有效数据')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/<int:role_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_role')
def delete_role(role_id):
    try:
        user = get_jwt_identity()
        update_dict = {
            'status': False,
            'updater': user.get('user_id')
        }
        stmt = update(Role).where(Role.role_id == role_id, Role.status == True).values(**update_dict)
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount:
            return jsonify(errcode=0, message='success')
        else:
            return jsonify(errcode=1, message='无有效数据')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/<int:role_id>', methods=['GET'])
@jwt_required()
@check_permission('get_roles')
def get_role(role_id):
    result = db.session.execute(select(Role.role_id, Role.role_code, Role.role_name
                                       ).where(Role.role_id == role_id)).first()
    role = result._asdict() if result else {}
    return jsonify(errcode=0, data=role)


@role_bp.route('/permissions', methods=['POST'])
@jwt_required()
@check_permission('create_permission')
def create_permission():
    try:
        permission = request.json
        if not isinstance(permission, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        permission_code = permission.get('permission_code')
        permission_name = permission.get('permission_name')
        if not permission_code or not permission_name:
            return jsonify(errcode=1, message='缺少必填项')
        if not isinstance(permission_code, str) or not isinstance(permission_name, str):
            return jsonify(errcode=1, message='数据类型不正确')
        permission_id = db.session.execute(
            select(Permission.permission_id).where(Permission.permission_code == permission_code,
                                                   Permission.status == True)).scalar()
        if permission_id:
            return jsonify(errcode=1, message='权限permission_code已存在')
        user = get_jwt_identity()
        insert_dict = {
            'permission_code': permission_code,
            'permission_name': permission_name,
            'creator': user.get('user_id'),
            'updater': user.get('user_id')
        }
        stmt = insert(Permission).values(**insert_dict)
        db.session.execute(stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/permissions/<int:permission_id>', methods=['PUT'])
@jwt_required()
@check_permission('update_permission')
def update_permission(permission_id):
    try:
        permission = request.json
        if not isinstance(permission, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        permission_code = permission.get('permission_code')
        permission_name = permission.get('permission_name')
        if not permission_code or not permission_name:
            return jsonify(errcode=1, message='缺少必填项')
        if not isinstance(permission_code, str) or not isinstance(permission_name, str):
            return jsonify(errcode=1, message='数据类型不正确')
        current_permission_id = db.session.execute(
            select(Permission.permission_id).where(Permission.permission_code == permission_code,
                                                   Permission.status == True)).scalar()
        if current_permission_id and current_permission_id != permission_id:
            return jsonify(errcode=1, message='权限permission_code已存在')
        user = get_jwt_identity()
        update_dict = {
            'permission_code': permission_code,
            'permission_name': permission_name,
            'updater': user.get('user_id')
        }
        stmt = update(Permission).where(Permission.permission_id == permission_id,
                                        Permission.status == True).values(**update_dict)
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount:
            return jsonify(errcode=0, message='success')
        else:
            return jsonify(errcode=1, message='无有效数据')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/permissions/<int:permission_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_permission')
def delete_permission(permission_id):
    try:
        user = get_jwt_identity()
        update_dict = {
            'status': False,
            'updater': user.get('user_id')
        }
        stmt = update(Permission).where(Permission.permission_id == permission_id,
                                        Permission.status == True).values(**update_dict)
        result = db.session.execute(stmt)
        db.session.commit()
        if result.rowcount:
            return jsonify(errcode=0, message='success')
        else:
            return jsonify(errcode=1, message='无有效数据')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/permissions/<int:permission_id>', methods=['GET'])
@jwt_required()
@check_permission('get_permissions')
def get_permission(permission_id):
    result = db.session.execute(select(Permission.permission_id, Permission.permission_code, Permission.permission_name
                                       ).where(Permission.permission_id == permission_id)).first()
    permission = result._asdict() if result else {}
    return jsonify(errcode=0, data=permission)


@role_bp.route('/<int:role_id>/permissions', methods=['POST', 'PUT'])
@jwt_required()
@check_permission('config_role_permissions')
def config_role_permissions(role_id):
    try:
        permission_ids = request.json
        if not isinstance(permission_ids, list) or not all(isinstance(item, int) for item in permission_ids):
            return jsonify(errcode=1, message='数据不正确')
        valid_permission_ids = db.session.execute(
            select(Permission.permission_id).where(Permission.status == True,
                                                   Permission.permission_id.in_(permission_ids))).scalars().all()
        if sorted(permission_ids) != sorted(valid_permission_ids):
            return jsonify(errcode=1, message='数据不正确')
        user = get_jwt_identity()
        updater = user['user_id']
        # 查询原有数据permission_ids
        select_stmt = select(RolePermission.permission_id).where(RolePermission.role_id == role_id,
                                                                 RolePermission.status == True)
        pre_permission_ids = db.session.execute(select_stmt).scalars().all()
        delete_permission_ids = list(set(pre_permission_ids) - set(permission_ids))
        update_permission_ids = list(set(pre_permission_ids) & set(permission_ids))  # 不做处理
        insert_permission_ids = list(set(permission_ids) - set(pre_permission_ids))
        # 无效删除的数据
        update_stmt = update(RolePermission).where(
            RolePermission.role_id == role_id, RolePermission.status == True,
            RolePermission.permission_id.in_(delete_permission_ids)
        ).values(status=False, updater=updater)
        # 插入数据
        insert_dict = {
            'role_id': role_id,
            'creator': updater,
            'updater': updater
        }
        insert_stmt = insert(RolePermission).values(**insert_dict)
        insert_permissions = [{'permission_id': permission_id} for permission_id in insert_permission_ids]
        db.session.execute(update_stmt)
        if insert_permissions:
            db.session.execute(insert_stmt, insert_permissions)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        return jsonify(errcode=1, message=str(e)), 500


@role_bp.route('/<int:role_id>/permissions', methods=['GET'])
@jwt_required()
@check_permission('get_role_permissions')
def get_role_permissions(role_id):
    query = select(Permission.permission_id, Permission.permission_code, Permission.permission_name
                   ).join_from(Permission, RolePermission, Permission.permission_id == RolePermission.permission_id
                               ).where(RolePermission.role_id == role_id, RolePermission.status == True)
    results = db.session.execute(query).all()
    permissions = []
    for result in results:
        permissions.append(result._asdict())
    return jsonify(errcode=0, data=permissions)
