#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/14 11:33
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, and_, or_

from exts import db


class Module(db.Model):
    module_id = Column(Integer, primary_key=True)
    module_code = Column(String(100), unique=True, nullable=False)
    module_name = Column(String(100), unique=True, nullable=False)
    description = Column(String(200))
    parent_module_id = Column(Integer, default=0)
    project_id = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def get_module(module_id):
        result = db.session.execute(select(Module.module_id, Module.module_code, Module.module_name, Module.project_id)
                                    .where(Module.module_id == module_id, Module.status == True)).first()
        return result._asdict() if result else {}

    @staticmethod
    def check_module(module_id, project_id):
        result = db.session.execute(
            select(Module.module_id).where(
                Module.module_id == module_id, Module.project_id == project_id, Module.status == True
            )
        ).first()
        return True if result else False

    @staticmethod
    def search_modules(project_id, keyword):
        results = db.session.execute(select(Module.module_id, Module.module_code, Module.module_name)
                                     .where(Module.project_id == project_id, Module.status == True,
                                            or_(Module.module_code.like('%%{}%%'.format(keyword)),
                                                Module.module_name.like('%%{}%%'.format(keyword))))).all()
        return [result._asdict() for result in results]

    @staticmethod
    def get_modules(project_id):
        results = db.session.execute(select(Module.module_id, Module.module_code, Module.module_name)
                                     .where(Module.project_id == project_id, Module.status == True)).all()
        return [result._asdict() for result in results]

