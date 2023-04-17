#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/21 18:26
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import Column, Integer, String, TIMESTAMP, func, Boolean, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from exts import db


class Role(db.Model):
    role_id = Column(Integer, primary_key=True)
    role_code = Column(String(50), unique=True, nullable=False)
    role_name = Column(String(100), unique=True, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
    permissions = relationship('Permission', secondary='role_permission')


class Permission(db.Model):
    permission_id = Column(Integer, primary_key=True)
    permission_code = Column(String(50), unique=True, nullable=False)
    permission_name = Column(String(100), unique=True, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)


class RolePermission(db.Model):
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('role.role_id'))
    permission_id = Column(Integer, ForeignKey('permission.permission_id'))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', 'status', name='_role_permission_uc'),
    )

