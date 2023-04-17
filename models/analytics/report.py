#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:55
# author: fengqiyuan
from datetime import datetime

from sqlalchemy import func, insert, update, select, Column, Integer, String, TIMESTAMP, Boolean

from common.logger import logger
from exts import db


class Report(db.Model):
    report_id = Column(Integer, primary_key=True)
    report_name = Column(String(100), nullable=False)
    project_id = Column(Integer, nullable=False)
    source = Column(String(10), nullable=False)
    env_id = Column(Integer, nullable=False)
    duration = Column(Integer)
    total = Column(Integer)
    passed_total = Column(Integer)
    failed_total = Column(Integer)
    skipped_total = Column(Integer)
    description = Column(String(200))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer, nullable=False)
    updater = Column(Integer, nullable=False)
    status = Column(Boolean, default=True)

    @staticmethod
    def create_report(insert_dict):
        try:
            stmt = insert(Report).values(**insert_dict)
            result = db.session.execute(stmt)
            db.session.commit()
            return result.inserted_primary_key[0]
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def update_report(report_id, update_dict):
        try:
            stmt = update(Report).where(Report.report_id == report_id).values(**update_dict)
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def delete_report(report_id):
        try:
            stmt = update(Report).where(Report.report_id == report_id).values(status=False, update_time=func.now())
            db.session.execute(stmt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_report(report_id):
        try:
            stmt = select(Report.report_id, Report.report_name, Report.project_id, Report.source, Report.env_id
                          ).where(Report.report_id == report_id, Report.status == True)
            result = db.session.execute(stmt).first()
            report = result._asdict() if result else {}
            db.session.commit()
            return report
        except Exception as e:
            db.session.rollback()
            raise

    @classmethod
    def get_report_statistics(cls):
        result = db.session.execute(
            select(func.sum(cls.duration), func.sum(cls.total), func.sum(cls.passed_total),
                   func.sum(cls.failed_total), func.sum(cls.skipped_total),
                   func.sum(cls.duration) // func.sum(cls.total)).filter(cls.status == True)).first()
        keys = ['duration', 'total', 'passed_total', 'failed_total', 'skipped_total', 'average']
        return dict(zip(keys, result))
