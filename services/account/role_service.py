#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/4/12 01:51
# author: fengqiyuan
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import select
from sqlalchemy import inspect
from models.account.role import Permission, RolePermission, db
from models.account.user_role import UserProjectRole, UserRole
from models.config.project import Project


def check_permission(permission_code, scope=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()
            user_id = user.get('user_id')
            if not has_permission(user_id, permission_code, scope):
                return jsonify(errcode=1, message='无权限')
            return func(*args, **kwargs)

        return wrapper

    return decorator


def has_permission(user_id, permission_code, scope):
    if scope is None or scope == 'system':
        query = select(UserRole.role_id
                       ).join_from(UserRole, RolePermission, UserRole.role_id == RolePermission.role_id) \
            .join(Permission, RolePermission.permission_id == Permission.permission_id) \
            .where(UserRole.user_id == user_id, Permission.permission_code == permission_code, UserRole.status == True,
                   RolePermission.status == True)
        role_id = db.session.execute(query).scalar()
        return True if role_id else False
    elif scope == 'project':
        query = select(UserProjectRole.role_id
                       ).join_from(UserProjectRole, RolePermission, UserProjectRole.role_id == RolePermission.role_id) \
            .join(Permission, RolePermission.permission_id == Permission.permission_id) \
            .join(Project, UserProjectRole.project_id == Project.project_id) \
            .where(UserProjectRole.user_id == user_id, Permission.permission_code == permission_code,
                   UserProjectRole.status == True, RolePermission.status == True, Project.status == True
                   )
        role_id = db.session.execute(query).scalar()
        return True if role_id else False
    else:
        return False


def get_project_role_project_ids(user_id, permission_code):
    query = select(UserProjectRole.project_id
                   ).join_from(UserProjectRole, RolePermission, UserProjectRole.role_id == RolePermission.role_id) \
        .join(Permission, RolePermission.permission_id == Permission.permission_id) \
        .join(Project, UserProjectRole.project_id == Project.project_id) \
        .where(UserProjectRole.user_id == user_id, Permission.permission_code == permission_code,
               UserProjectRole.status == True, RolePermission.status == True, Project.status == True)
    project_ids = db.session.execute(query).scalars().all()
    return project_ids


def check_project_permission(user_id, project_id, permission_code):
    query = select(UserProjectRole.role_id
                   ).join_from(UserProjectRole, RolePermission, UserProjectRole.role_id == RolePermission.role_id) \
        .join(Permission, RolePermission.permission_id == Permission.permission_id) \
        .join(Project, UserProjectRole.project_id == Project.project_id) \
        .where(UserProjectRole.user_id == user_id, Permission.permission_code == permission_code,
               Project.project_id == project_id, UserProjectRole.status == True, RolePermission.status == True,
               Project.status == True
               )
    role_id = db.session.execute(query).scalar()
    return True if role_id else False


def check_model_permission(user_id, model_class, model_id, permission_code):
    # 获取类
    # model_class = globals()[model_name]

    # 获取主键名称
    primary_key = inspect(model_class).primary_key[0].name

    # 查询权限
    query = select(UserProjectRole.role_id). \
        join(RolePermission, RolePermission.role_id == UserProjectRole.role_id). \
        join(Permission, Permission.permission_id == RolePermission.permission_id). \
        join(Project, Project.project_id == UserProjectRole.project_id). \
        join(model_class, model_class.project_id == Project.project_id). \
        where(
        UserProjectRole.user_id == user_id,
        Permission.permission_code == permission_code,
        getattr(model_class, primary_key) == model_id,
        UserProjectRole.status == True,
        RolePermission.status == True,
        Permission.status == True,
        Project.status == True,
        model_class.status == True
    )

    role_id = db.session.execute(query).scalar()
    return True if role_id else False
