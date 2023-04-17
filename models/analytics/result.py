#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/10 21:13
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, JSON, null

from common.logger import logger
from exts import db


class Result(db.Model):
    result_id = Column(Integer, primary_key=True)
    testcase_id = Column(Integer, nullable=False)
    execute_status = Column(Integer, nullable=False)
    actual_result = Column(JSON, nullable=False, default=null())
    project_id = Column(Integer)
    testsuite_id = Column(Integer)
    runner_id = Column(Integer)
    report_id = Column(Integer)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def create_result(result_list, creator):
        try:
            db.session.execute(insert(Result).values(creator=creator, updater=creator), result_list)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()

    @staticmethod
    def create_report_result(insert_dict, result_list):
        try:
            db.session.execute(insert(Result).values(**insert_dict), result_list)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()



