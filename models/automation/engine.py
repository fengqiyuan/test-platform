#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/14 10:44
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean
from exts import db


class Engine(db.Model):
    engine_id = Column(Integer, primary_key=True)
    engine_name = Column(String(100), unique=True, nullable=False)
    secret = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    description = Column(String(200))
    project_id = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(db.Boolean, default=True)

