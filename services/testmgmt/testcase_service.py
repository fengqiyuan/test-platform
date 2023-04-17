#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 08:38
# author: fengqiyuan
import json

from sqlalchemy import select
from sqlalchemy.orm import Bundle, aliased

from models.testmgmt.testcase import TestCase, db
from models.config.module import Module
from models.config.project import Project
from models.testmgmt.testscenario import TestScenario
from models.account.user import User
from models.testmgmt.testsuite import TestSuiteDetail


class TestCaseService:

    @staticmethod
    def get_testcase(testcase_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("testcase", TestCase.testcase_id, TestCase.testcase_name, TestCase.test_type,
                        TestCase.test_priority, TestCase.pre_process, TestCase.test_content,
                        TestCase.test_data, TestCase.post_process, TestCase.expected_result, TestCase.actual_result,
                        TestCase.description, TestScenario.scenario_id, TestScenario.scenario_code,
                        TestScenario.scenario_name, TestScenario.scenario_level, TestScenario.scenario_type,
                        TestScenario.project_id, Project.project_name, TestScenario.module_id,
                        Module.module_name, TestCase.creator, TestCase.updater, TestCase.create_time,
                        TestCase.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(TestCase, TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .join(Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Module, Module.module_id == TestScenario.module_id) \
            .outerjoin(creator, creator.user_id == TestCase.creator) \
            .outerjoin(updater, updater.user_id == TestCase.updater) \
            .where(TestCase.testcase_id == testcase_id, TestCase.status == True)

        result = db.session.execute(query).scalars().first()
        testcase = result._asdict() if result else {}
        return testcase

    @staticmethod
    def get_scenario_testcases(scenario_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("testcase", TestCase.testcase_id, TestCase.testcase_name, TestCase.test_type,
                        TestCase.test_priority, TestCase.pre_process, TestCase.test_content,
                        TestCase.test_data, TestCase.post_process, TestCase.expected_result, TestCase.actual_result,
                        TestCase.description, TestCase.project_id, TestCase.scenario_id, TestCase.creator,
                        TestCase.updater, TestCase.create_time, TestCase.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(TestCase, TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .outerjoin(creator, creator.user_id == TestCase.creator) \
            .outerjoin(updater, updater.user_id == TestCase.updater) \
            .where(TestCase.scenario_id == scenario_id, TestCase.status == True)

        result = db.session.execute(query).scalars()
        testcases = []
        for item in result:
            testcase = item._asdict()
            testcases.append(testcase)
        return testcases

    @staticmethod
    def get_project_testcases(project_id, keyword):
        bundle = Bundle("testcase", TestCase.testcase_id, TestCase.testcase_name, TestCase.test_type,
                        TestCase.test_priority, TestCase.pre_process, TestCase.test_content,
                        TestCase.test_data, TestCase.post_process, TestCase.expected_result, TestCase.actual_result,
                        TestCase.description, TestScenario.scenario_id, TestScenario.scenario_code,
                        TestScenario.scenario_name, TestScenario.scenario_level, TestScenario.scenario_type,
                        TestScenario.project_id, Project.project_name, TestScenario.module_id,
                        Module.module_name
                        )
        query = select(bundle).join_from(TestCase, TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .join(Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Module, Module.module_id == TestScenario.module_id) \
            .where(TestScenario.project_id == project_id, TestCase.status == True,
                   TestCase.testcase_name.like('%%{}%%'.format(keyword)))

        result = db.session.execute(query).scalars()
        testcases = []
        for item in result:
            testcase = item._asdict()
            testcases.append(testcase)
        return testcases

    @staticmethod
    def get_execute_testcases(testcase_id):
        bundle = Bundle("testcase", TestCase.testcase_id, TestCase.testcase_name, TestCase.test_type,
                        TestCase.test_priority, TestCase.pre_process, TestCase.test_content, TestCase.test_data,
                        TestCase.post_process, TestCase.expected_result, TestCase.actual_result, TestCase.project_id,
                        TestCase.scenario_id
                        )
        query = select(bundle).select_from(TestCase).where(TestCase.testcase_id == testcase_id, TestCase.status == True)

        result = db.session.execute(query).scalar()
        testcase = result._asdict() if result else {}
        return testcase

    @staticmethod
    def get_scenario_execute_testcases(scenario_id):
        bundle = Bundle("testcase", TestCase.testcase_id, TestCase.testcase_name, TestCase.test_type,
                        TestCase.test_priority, TestCase.pre_process, TestCase.test_content, TestCase.test_data,
                        TestCase.post_process, TestCase.expected_result, TestCase.actual_result, TestCase.project_id,
                        TestCase.scenario_id
                        )
        query = select(bundle).join_from(TestCase, TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .where(TestCase.scenario_id == scenario_id, TestCase.status == True)

        result = db.session.execute(query).scalars()
        testcases = []
        for item in result:
            testcase = item._asdict()
            testcases.append(testcase)
        return testcases

    @staticmethod
    def get_testsuite_execute_testcases(testsuite_id):
        bundle = Bundle("testcase", TestCase.testcase_id, TestCase.testcase_name, TestCase.test_type,
                        TestCase.test_priority, TestCase.pre_process, TestCase.test_content, TestCase.test_data,
                        TestCase.post_process, TestCase.expected_result, TestCase.actual_result, TestCase.project_id,
                        TestCase.scenario_id, TestSuiteDetail.testsuite_id, TestSuiteDetail.execute_type,
                        TestSuiteDetail.order
                        )
        query = select(bundle).join_from(
            TestCase, TestSuiteDetail, TestCase.testcase_id == TestSuiteDetail.testcase_id
        ).where(TestSuiteDetail.testsuite_id == testsuite_id,
                TestSuiteDetail.status == True).order_by(TestSuiteDetail.order)

        result = db.session.execute(query).scalars()
        flow_testcases, single_testcases = [], []
        for item in result:
            testcase = item._asdict()
            if testcase['order'] > 0:
                flow_testcases.append(testcase)
            else:
                single_testcases.append(testcase)
        return flow_testcases, single_testcases



