#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:51
# author: fengqiyuan
import json
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean

from common.logger import logger
from exts import db


class TestSuite(db.Model):
    testsuite_id = Column(Integer, primary_key=True)
    testsuite_name = Column(String(100), unique=True, nullable=False)
    project_id = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    single_total = Column(Integer, nullable=False)
    execute_time = Column(TIMESTAMP)
    execute_status = Column(Integer)
    description = Column(String(200))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @classmethod
    def get_testsuite_statistics(cls):
        result = db.session.execute(select(func.sum(cls.total), func.sum(cls.single_total),
                                           func.sum(cls.total) - func.sum(cls.single_total),
                                           func.count(cls.testsuite_id)
                                           ).filter(cls.status == True)).first()
        keys = ['testcase_total', 'testcase_single_total', 'testcase_flow_total', 'flow_total']
        return dict(zip(keys, result))


class TestSuiteDetail(db.Model):
    id = Column(Integer, primary_key=True)
    testsuite_id = Column(Integer, nullable=False)
    testcase_id = Column(Integer, nullable=False)
    execute_type = Column(Boolean, nullable=False)
    order = Column(Integer)
    create_time = Column(TIMESTAMP, default=func.now())
    update_time = Column(TIMESTAMP, default=func.now())
    creator = Column(Integer, nullable=False, default=1)
    updater = Column(Integer, nullable=False, default=1)
    status = Column(Boolean, default=True)


