#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:53
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, and_, or_, DateTime
from sqlalchemy.orm import Bundle, relationship

from exts import db
from models.account.user_role import UserProjectRole


class Project(db.Model):
    project_id = Column(Integer, primary_key=True)
    project_code = Column(String(50), nullable=False)
    project_name = Column(String(100), unique=True, nullable=False)
    git_url = Column(String(100), nullable=False)
    description = Column(String(200))
    create_time = Column(TIMESTAMP(timezone=True), default=func.now())
    update_time = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
    users = relationship('User', secondary=UserProjectRole.__table__, back_populates='projects')

    @staticmethod
    def get_project(project_id):
        result = db.session.execute(
            select(Project.project_id, Project.project_code, Project.project_name, Project.git_url, Project.create_time,
                   Project.update_time).where(Project.project_id == project_id, Project.status == True)
        ).first()
        return result._asdict() if result else {}

    @staticmethod
    def search_project(query, project_ids):
        results = db.session.execute(
            select(Project.project_id, Project.project_code, Project.project_name).where(
                Project.status == True, Project.project_id.in_(project_ids),
                or_(Project.project_code.like('%%{}%%'.format(query)),
                    Project.project_name.like('%%{}%%'.format(query))))).all()
        return [result._asdict() for result in results]
