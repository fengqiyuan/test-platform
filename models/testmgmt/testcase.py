#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/14 14:17
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, JSON, null, text
from common.logger import logger
from exts import db


class TestCase(db.Model):
    testcase_id = Column(Integer, primary_key=True)
    testcase_name = Column(String(100), unique=True, nullable=False)
    test_type = Column(String(10), nullable=False)
    test_priority = Column(Integer, nullable=False)
    test_data = Column(JSON, default=null())
    pre_process = Column(JSON, default=null())
    test_content = Column(JSON, default=null(), nullable=False)
    post_process = Column(JSON, default=null())
    expected_result = Column(JSON, nullable=False)
    execute_time = Column(TIMESTAMP)
    execute_status = Column(Integer)
    actual_result = Column(JSON, default=null())
    description = Column(String(200))
    project_id = Column(Integer, nullable=False)
    scenario_id = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def create_testcase(insert_dict):
        try:
            stmt = insert(TestCase).values(**insert_dict)
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def update_testcase(testcase_id, update_dict):
        try:
            stmt = update(TestCase).where(TestCase.testcase_id == testcase_id, TestCase.status == True
                                          ).values(**update_dict)
            db.session.execute(stmt)
            # None时更新为null
            if not update_dict['pre_process']:
                db.session.execute(text(f'UPDATE test_case SET pre_process=null WHERE testcase_id = {testcase_id}'))
            if not update_dict['test_data']:
                db.session.execute(text(f'UPDATE test_case SET test_data=null WHERE testcase_id = {testcase_id}'))
            if not update_dict['post_process']:
                db.session.execute(text(f'UPDATE test_case SET post_process=null WHERE testcase_id = {testcase_id}'))
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def bulk_update_testcases(update_dict_list, updater):
        try:
            db.session.execute(update(TestCase).values(updater=updater), update_dict_list)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def check_testcase_id(testcase_id):
        result = db.session.execute(
            select(TestCase.testcase_id).where(TestCase.testcase_id == testcase_id, TestCase.status == True)
        ).scalar()
        return True if result else False

    @classmethod
    def get_testcase_statistics(cls):
        result = db.session.execute(select(cls.test_type, cls.test_priority, func.count(cls.testcase_id))
                                    .filter(cls.status == True)
                                    .group_by(cls.test_type, cls.test_priority)
                                    .order_by(cls.test_type, cls.test_priority))
        data = {}
        for item in result:
            key1, key2, value = item
            if key1 not in data:
                data[key1] = {}
            data[key1][str(key2)] = value
        return data
