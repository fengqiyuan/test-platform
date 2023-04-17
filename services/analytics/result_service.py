#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:33
# author: fengqiyuan
from sqlalchemy import select, String
from sqlalchemy.orm import aliased, Bundle

from models.account.user import User
from models.analytics.report import Report
from models.analytics.result import Result, db
from models.automation.runner import Runner
from models.config.project import Project
from models.testmgmt.testcase import TestCase
from models.testmgmt.testscenario import TestScenario
from models.testmgmt.testsuite import TestSuite


class ResultService:

    @staticmethod
    def get_result(report_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("result", Result.result_id, Result.report_id, Report.report_name, Result.runner_id,
                        Runner.runner_name, Result.testsuite_id, TestSuite.testsuite_name, TestScenario.scenario_id,
                        TestScenario.scenario_name, TestScenario.project_id, Project.project_name,
                        Result.testcase_id, TestCase.testcase_name, Result.execute_status, Result.actual_result,
                        Result.create_time, Result.update_time, Result.creator, Result.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Result, TestCase, TestCase.testcase_id == Result.testcase_id) \
            .join(TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .join(Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Report, Report.report_id == Result.report_id) \
            .outerjoin(TestSuite, TestSuite.testsuite_id == Result.testsuite_id) \
            .outerjoin(Runner, Runner.runner_id == Result.runner_id) \
            .outerjoin(creator, creator.user_id == Result.creator) \
            .outerjoin(updater, updater.user_id == Result.updater) \
            .where(Result.report_id == report_id, Result.status == True)

        result = db.session.execute(query).scalars()
        data = [item._asdict() for item in result if result]
        return data

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("result", Result.result_id, Result.report_id, Report.report_name, Result.runner_id,
                        Runner.runner_name, Result.testsuite_id, TestSuite.testsuite_name, TestScenario.scenario_id,
                        TestScenario.scenario_name, TestScenario.project_id, Project.project_name, Result.testcase_id,
                        TestCase.testcase_name, Result.execute_status, Result.actual_result.cast(String),
                        Result.create_time, Result.update_time, Result.creator, Result.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Result, TestCase, TestCase.testcase_id == Result.testcase_id) \
            .join(TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .join(Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Report, Report.report_id == Result.report_id) \
            .outerjoin(TestSuite, TestSuite.testsuite_id == Result.testsuite_id) \
            .outerjoin(Runner, Runner.runner_id == Result.runner_id) \
            .outerjoin(creator, creator.user_id == Result.creator) \
            .outerjoin(updater, updater.user_id == Result.updater) \
            .where(Result.status == True, Project.project_id.in_(project_ids)).order_by(Result.result_id.desc())

        results = db.paginate(query, page=page_no, per_page=page_size)
        data, total, page_total, iter_pages = [], 0, 0, []
        if results:
            data = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return data, total, page_total, iter_pages
