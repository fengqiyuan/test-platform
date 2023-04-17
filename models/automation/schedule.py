#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/14 15:07
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean

from common.logger import logger
from exts import db


class Schedule(db.Model):
    schedule_id = Column(Integer, primary_key=True)
    schedule_name = Column(String(100), unique=True, nullable=False)
    project_id = Column(Integer, nullable=False)
    runner_id = Column(Integer, nullable=False)
    cron = Column(String(100), nullable=False)
    execute_time = Column(TIMESTAMP)
    execute_status = Column(Boolean, default=True)
    description = Column(String(500))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def create_schedule(insert_dict):
        try:
            stmt = insert(Schedule).values(**insert_dict)
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def update_schedule(schedule_id, update_dict):
        try:
            stmt = update(Schedule).where(Schedule.schedule_id == schedule_id)
            db.session.execute(stmt, update_dict)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise


