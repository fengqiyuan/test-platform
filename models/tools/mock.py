#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/1 07:41
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean
from exts import db


class Mock(db.Model):
    mock_id = Column(Integer, primary_key=True)
    mock_code = Column(String(255))
    mock_name = Column(String(255), nullable=False)
    project_id = Column(Integer, nullable=False)
    module_id = Column(Integer)
    env_id = Column(Integer, nullable=False)
    url = Column(String(100), nullable=False)
    path = Column(String(50), nullable=False)
    method = Column(String(10), nullable=False)
    params = Column(String(1000))
    authorization = Column(String(1000))
    headers = Column(String(1000))
    data = Column(String(1000))
    response_status = Column(Integer, nullable=False)
    response_headers = Column(String(1000), nullable=False)
    response_data = Column(String(1000))
    description = Column(String(200))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def get_mock_data_path(path, method):
        results = db.session.execute(select(Mock.url, Mock.params, Mock.headers, Mock.data,
                                            Mock.response_status, Mock.response_headers, Mock.response_data).where(
            Mock.path == path, Mock.method == method)).scalars()
        return results
