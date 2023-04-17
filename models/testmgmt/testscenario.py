#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 09:50
# author: fengqiyuan
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, or_
from exts import db


class TestScenario(db.Model):
    scenario_id = Column(Integer, primary_key=True)
    scenario_code = Column(String(100), nullable=False)
    scenario_name = Column(String(100), unique=True, nullable=False)
    scenario_level = Column(Integer, nullable=False)
    scenario_type = Column(String(20), nullable=False)
    execute_time = Column(TIMESTAMP)
    execute_status = Column(Integer)
    description = Column(String(200))
    project_id = Column(Integer, nullable=False)
    module_id = Column(Integer)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def create_scenario(insert_dict):
        try:
            stmt = insert(TestScenario).values(**insert_dict)
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def update_scenario(scenario_id, update_dict):
        try:
            db.session.execute(
                update(TestScenario).where(
                    TestScenario.scenario_id == scenario_id, TestScenario.status == True
                ).values(**update_dict)
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def check_scenario_id(scenario_id):
        result = db.session.execute(
            select(TestScenario.scenario_id).where(TestScenario.scenario_id == scenario_id, TestScenario.status == True)
        ).scalar()
        return True if result else False

    @staticmethod
    def search_scenario(query):
        results = db.session.execute(
            select(TestScenario.scenario_id, TestScenario.scenario_code, TestScenario.scenario_name
                   ).where(
                or_(TestScenario.scenario_code.like('%%{}%%'.format(query)),
                    TestScenario.scenario_name.like('%%{}%%'.format(query)))
            )
        ).all()
        return [result._asdict() for result in results]

    @classmethod
    def get_testscenario_statistics(cls):

        result = db.session.execute(select(cls.scenario_type, cls.scenario_level, func.count(cls.scenario_id))
                                    .filter(cls.status == True)
                                    .group_by(cls.scenario_type, cls.scenario_level)
                                    .order_by(cls.scenario_type, cls.scenario_level))
        data = {}
        for item in result:
            key1, key2, value = item
            if key1 not in data:
                data[key1] = {}
            data[key1][str(key2)] = value
        print(data)
        return data
