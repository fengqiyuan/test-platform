#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/13 17:17
# author: fengqiyuan
from dataclasses import dataclass, asdict
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean, and_, or_, JSON, null
from sqlalchemy.orm import Bundle

from exts import db


@dataclass
class Environment(db.Model):
    env_id: int = Column(Integer, primary_key=True)
    env_name: str = Column(String(100), unique=True, nullable=False)
    protocol: str = Column(String(20), nullable=False)
    hostname: str = Column(String(100), nullable=False)
    port: int = Column(Integer, nullable=False)
    env_url: str = Column(String(200), nullable=False)
    db_config: dict = Column(JSON, default=null())
    redis_config: dict = Column(JSON, default=null())
    description: str = Column(String(200))
    project_id: int = Column(Integer, nullable=False)
    create_time: str = Column(TIMESTAMP, default=datetime.now)
    update_time: str = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator: int = Column(Integer, nullable=False)
    updater: int = Column(Integer, nullable=False)
    status: bool = Column(Boolean, default=True)

    @staticmethod
    def get_environment(env_id):
        env = db.session.execute(
            select(Environment).where(Environment.env_id == env_id, Environment.status == True)
        ).scalar()
        return env

    @staticmethod
    def get_environment_dict(env_id):
        env = db.session.execute(
            select(Environment).where(Environment.env_id == env_id, Environment.status == True)
        ).scalar()
        return asdict(env) if env else None

    @staticmethod
    def search_environment(project_id, keyword):
        results = db.session.execute(
            select(Environment.env_id, Environment.env_name, Environment.env_url)
            .where(Environment.project_id == project_id, Environment.status == True,
                   or_(Environment.env_name.like('%%{}%%'.format(keyword)),
                       Environment.env_url.like('%%{}%%'.format(keyword))))
        ).all()
        return [result._asdict() for result in results]

    @staticmethod
    def get_environments(project_id):
        results = db.session.execute(
            select(
                Environment.env_id, Environment.env_name, Environment.env_url
            ).where(Environment.project_id == project_id, Environment.status == True)
        ).all()
        return [result._asdict() for result in results]
