#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/21 19:56
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, func, Boolean
from sqlalchemy.orm import relationship

from exts import db


class UserRole(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    role_id = Column(Integer, ForeignKey('role.role_id'))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
    role = relationship('Role')


class UserProjectRole(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.user_id'))
    project_id = Column(Integer, ForeignKey('project.project_id'))
    role_id = Column(Integer, ForeignKey('role.role_id'))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
    role = relationship('Role')
