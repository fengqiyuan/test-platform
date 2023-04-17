#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/14 10:56
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, FLOAT
from exts import db


class Statistics(db.Model):
    statistics_id = Column(Integer, primary_key=True)
    statistics_name = Column(String(100), unique=True, nullable=False)
    stat_type = Column(String(20), nullable=False)
    stat_date = Column(db.DateTime, nullable=False)
    api_case_new = Column(Integer, nullable=False)
    web_case_new = Column(Integer, nullable=False)
    app_case_new = Column(Integer, nullable=False)
    case_new = Column(Integer, nullable=False)
    api_case_total = Column(Integer, nullable=False)
    web_case_total = Column(Integer, nullable=False)
    app_case_total = Column(Integer, nullable=False)
    case_total = Column(Integer, nullable=False)
    api_case_run_total = Column(Integer, nullable=False)
    web_case_run_total = Column(Integer, nullable=False)
    app_case_run_total = Column(Integer, nullable=False)
    case_run_total = Column(Integer, nullable=False)
    api_case_pass_rate = Column(FLOAT, nullable=False)
    web_case_pass_rate = Column(FLOAT, nullable=False)
    app_case_pass_rate = Column(FLOAT, nullable=False)
    case_pass_rate = Column(FLOAT, nullable=False)
    api_bug_total = Column(Integer, nullable=False)
    web_bug_total = Column(Integer, nullable=False)
    app_bug_total = Column(Integer, nullable=False)
    bug_total = Column(Integer, nullable=False)
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)
