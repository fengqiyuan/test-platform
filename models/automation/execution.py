#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:55
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean
from exts import db


class Execution(db.Model):
    exec_id = Column(Integer, primary_key=True)
    exec_name = Column(String(100), unique=True, nullable=False)
    exec_type = Column(String(20), nullable=False)
    execute_time = Column(TIMESTAMP)
    execute_status = Column(Integer)
    description = Column(String(200))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
