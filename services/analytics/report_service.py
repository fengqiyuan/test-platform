#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/26 08:46
# author: fengqiyuan
from sqlalchemy import select
from sqlalchemy.orm import Bundle, aliased

from models.account.user import User
from models.analytics.report import Report, db
from models.config.environment import Environment
from models.config.project import Project


class ReportService:

    @staticmethod
    def create_report(report):
        report_name = report.get('report_name', '')
        project_id = report.get('project_id', 0)
        source = report.get('source', '')
        env_id = report.get('env_id', 0)
        duration = report.get('duration', 0)
        total = report.get('total', 0)
        passed_total = report.get('passed_total', 0)
        failed_total = report.get('failed_total', 0)
        skipped_total = report.get('skipped_total', 0)
        if report and report_name and project_id and source and env_id and duration and total:
            insert_dict = {
                'report_name': report_name,
                'project_id': project_id,
                'source': source,
                'env_id': env_id,
                'duration': duration,
                'total': total,
                'passed_total': passed_total,
                'failed_total': failed_total,
                'skipped_total': skipped_total
            }
            report_id = Report.create_report(insert_dict)
            return report_id
        else:
            raise KeyError("缺少必填字段")

    @staticmethod
    def get_report(report_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("report", Report.report_id, Report.report_name, Report.project_id, Project.project_name,
                        Report.source, Report.env_id, Environment.env_name, Environment.env_url, Report.duration,
                        Report.total, Report.passed_total, Report.failed_total, Report.skipped_total,
                        Report.create_time, Report.update_time, Report.creator, Report.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Report, Project, Project.project_id == Report.project_id) \
            .join(Environment, Environment.env_id == Report.env_id) \
            .outerjoin(creator, creator.user_id == Report.creator) \
            .outerjoin(updater, updater.user_id == Report.updater) \
            .where(Report.report_id == report_id, Report.status == True)

        report = db.session.execute(query).scalars().first()
        return report._asdict() if report else {}

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("report", Report.report_id, Report.report_name, Report.project_id, Project.project_name,
                        Report.source, Report.env_id, Environment.env_name, Environment.env_url, Report.duration,
                        Report.total, Report.passed_total, Report.failed_total, Report.skipped_total,
                        Report.create_time, Report.update_time, Report.creator, Report.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Report, Project, Project.project_id == Report.project_id) \
            .join(Environment, Environment.env_id == Report.env_id) \
            .outerjoin(creator, creator.user_id == Report.creator) \
            .outerjoin(updater, updater.user_id == Report.updater) \
            .where(Report.status == True, Project.project_id.in_(project_ids)).order_by(Report.report_id.desc())

        results = db.paginate(query, page=page_no, per_page=page_size)
        reports, total, page_total, iter_pages = [], 0, 0, []
        if results:
            reports = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return reports, total, page_total, iter_pages

