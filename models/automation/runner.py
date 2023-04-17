#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:54
# author: fengqiyuan
from datetime import datetime
from sqlalchemy import func, update, select, Column, Integer, String, TIMESTAMP, Boolean
from exts import db


class Runner(db.Model):
    runner_id = Column(Integer, primary_key=True)
    runner_name = Column(String(100), unique=True, nullable=False)
    project_id = Column(Integer, nullable=False)
    env_id = Column(Integer, nullable=False)
    execute_time = Column(TIMESTAMP)
    execute_status = Column(Integer)
    description = Column(String(200))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def update_runner(runner_id, update_dict):
        try:
            stmt = update(Runner).where(Runner.runner_id == runner_id).values(**update_dict)
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_runner(runner_id):
        stmt = select(Runner.runner_id, Runner.runner_name, Runner.project_id, Runner.env_id
                      ).where(Runner.runner_id == runner_id, Runner.status == True)
        result = db.session.execute(stmt).first()
        runner = result._asdict() if result else {}
        return runner

    @staticmethod
    def search_runners(project_id, keyword):
        results = db.session.execute(select(Runner.runner_id, Runner.runner_name)
                                     .where(Runner.project_id == project_id,
                                            Runner.runner_name.like('%%{}%%'.format(keyword)))).all()
        return [result._asdict() for result in results]

    @classmethod
    def get_runner_statistics(cls):
        result = db.session.execute(select(cls.test_type, cls.test_priority, func.count(cls.testcase_id).label('total'))
                                    .where(cls.status == True)
                                    .group_by(cls.test_type, cls.test_priority)
                                    .order_by(cls.test_type, cls.test_priority)).first()
        return result._asdict() if result else {}


class RunnerTestSuite(db.Model):
    id = Column(Integer, primary_key=True)
    runner_id = Column(Integer, nullable=False)
    testsuite_id = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
