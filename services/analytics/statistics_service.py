#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/26 14:38
# author: fengqiyuan
from models.analytics.report import Report
from models.testmgmt.testcase import TestCase
from models.testmgmt.testscenario import TestScenario
from models.testmgmt.testsuite import TestSuite


class StatisticsService:

    @staticmethod
    def get_testscenario_statistics():
        data = TestScenario.get_testscenario_statistics()
        return data

    @staticmethod
    def get_testcase_statistics():
        data = TestCase.get_testcase_statistics()
        return data

    @staticmethod
    def get_testsuite_statistics():
        data = TestSuite.get_testsuite_statistics()
        return data

    @staticmethod
    def get_result_statistics():
        data = Report.get_report_statistics()
        print(data)
        return data

    @staticmethod
    def get_project_testscenario_statistics(project_id):
        pass

    @staticmethod
    def get_project_testcase_statistics(project_id):
        pass

    @staticmethod
    def get_project_testsuite_statistics(project_id):
        pass

    @staticmethod
    def get_project_result_statistics(project_id):
        pass
