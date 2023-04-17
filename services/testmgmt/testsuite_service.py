#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 09:45
# author: fengqiyuan
import json

from sqlalchemy import select, insert, update
from sqlalchemy.orm import aliased, Bundle

from common.logger import logger
from models.account.user import User
from models.config.module import Module
from models.config.project import Project
from models.testmgmt.testcase import TestCase
from models.testmgmt.testscenario import TestScenario
from models.testmgmt.testsuite import TestSuite, TestSuiteDetail, db


class TestSuiteService:

    @staticmethod
    def create_testsuite(insert_dict, insert_list, creator):
        try:
            result = db.session.execute(insert(TestSuite).values(creator=creator, updater=creator, **insert_dict))
            testsuite_id = result.inserted_primary_key[0]
            db.session.execute(
                insert(TestSuiteDetail).values(testsuite_id=testsuite_id, creator=creator, updater=creator),
                insert_list
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def update_testsuite(testsuite_id, update_dict, update_list, updater):
        try:
            db.session.execute(
                update(TestSuiteDetail).where(
                    TestSuiteDetail.testsuite_id == testsuite_id,
                    TestSuiteDetail.status == True
                ).values(status=False, updater=updater)
            )
            db.session.execute(
                update(TestSuite).where(
                    TestSuite.testsuite_id == testsuite_id, TestSuite.status == True
                ).values(updater=updater),
                update_dict
            )
            db.session.execute(
                insert(TestSuiteDetail).values(testsuite_id=testsuite_id, creator=updater, updater=updater),
                update_list
            )
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            raise

    @staticmethod
    def delete_testsuite(testsuite_id, updater):
        try:
            db.session.execute(
                update(TestSuite).where(
                    TestSuite.testsuite_id == testsuite_id, TestSuite.status == True
                ).values(status=False, updater=updater)
            )
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_testsuite(testsuite_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("testsuite", TestSuite.testsuite_id, TestSuite.testsuite_name, TestSuite.project_id,
                        Project.project_name, TestSuite.total, TestSuite.single_total, TestSuite.description,
                        TestSuite.create_time, TestSuite.update_time, TestSuite.creator, TestSuite.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(TestSuite, Project, Project.project_id == TestSuite.project_id) \
            .outerjoin(creator, creator.user_id == TestSuite.creator) \
            .outerjoin(updater, updater.user_id == TestSuite.updater) \
            .where(TestSuite.testsuite_id == testsuite_id, TestSuite.status == True)

        result = db.session.execute(query).scalars().first()
        return result._asdict() if result else {}

    @staticmethod
    def check_testsuite_id(testsuite_id):
        result = db.session.execute(
            select(TestSuite.testsuite_id).where(TestSuite.status == True, TestSuite.testsuite_id == testsuite_id)
        ).scalar()
        return True if result else False

    @staticmethod
    def check_testsuite_ids(testsuite_ids):
        valid_testsuite_ids = db.session.execute(
            select(TestSuite.testsuite_id).where(TestSuite.status == True, TestSuite.testsuite_id.in_(testsuite_ids))
        ).scalars().all()
        return True if sorted(valid_testsuite_ids) == sorted(testsuite_ids) else False

    @staticmethod
    def get_testsuites(id_list):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("testsuite", TestSuite.testsuite_id, TestSuite.testsuite_name, TestSuite.project_id,
                        Project.project_name, TestSuite.total, TestSuite.single_total, TestSuite.description,
                        TestSuite.create_time, TestSuite.update_time, TestSuite.creator, TestSuite.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(TestSuite, Project, Project.project_id == TestSuite.project_id) \
            .outerjoin(creator, creator.user_id == TestSuite.creator) \
            .outerjoin(updater, updater.user_id == TestSuite.updater) \
            .where(TestSuite.testsuite_id.in_(id_list), TestSuite.status == True)

        result = db.session.execute(query).scalars()
        return [item._asdict() for item in result if result]

    @staticmethod
    def get_project_testsuites(project_id, keyword):
        bundle = Bundle("testsuite", TestSuite.testsuite_id, TestSuite.testsuite_name, TestSuite.project_id,
                        Project.project_name, TestSuite.total, TestSuite.single_total, TestSuite.description
                        )
        query = select(bundle).join_from(TestSuite, Project, Project.project_id == TestSuite.project_id) \
            .where(TestSuite.project_id == project_id, TestSuite.status == True,
                   TestSuite.testsuite_name.like('%%{}%%'.format(keyword)))

        result = db.session.execute(query).scalars()
        testsuites = [item._asdict() for item in result if result]
        return testsuites

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("testsuite", TestSuite.testsuite_id, TestSuite.testsuite_name, TestSuite.project_id,
                        Project.project_name, TestSuite.total, TestSuite.single_total, TestSuite.description,
                        TestSuite.create_time, TestSuite.update_time, TestSuite.creator, TestSuite.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )

        query = select(bundle).join_from(TestSuite, Project, Project.project_id == TestSuite.project_id) \
            .outerjoin(creator, creator.user_id == TestSuite.creator) \
            .outerjoin(updater, updater.user_id == TestSuite.updater) \
            .where(TestSuite.status == True, TestSuite.project_id.in_(project_ids)
                   ).order_by(TestSuite.testsuite_id.desc())
        results = db.paginate(query, page=page_no, per_page=page_size)
        testsuites, total, page_total, iter_pages = [], 0, 0, []
        if results:
            testsuites = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return testsuites, total, page_total, iter_pages

    @staticmethod
    def get_testsuite_detail(testsuite_id):
        bundle = Bundle("testsuite", TestSuiteDetail.testsuite_id, TestSuiteDetail.testcase_id,
                        TestCase.testcase_name, TestSuiteDetail.execute_type, TestSuiteDetail.order,
                        TestCase.test_type, TestCase.test_priority, TestCase.test_content,
                        TestScenario.project_id, Project.project_name, TestScenario.module_id,
                        Module.module_name
                        )
        query = select(bundle) \
            .join_from(TestSuite, TestSuiteDetail, TestSuiteDetail.testsuite_id == TestSuite.testsuite_id) \
            .join(TestCase, TestCase.testcase_id == TestSuiteDetail.testcase_id) \
            .join(TestScenario, TestScenario.scenario_id == TestCase.scenario_id) \
            .join(Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Module, Module.module_id == TestScenario.module_id) \
            .where(TestSuiteDetail.testsuite_id == testsuite_id, TestSuiteDetail.status == True)

        result = db.session.execute(query).scalars()
        testcases = []
        for item in result:
            testcase = item._asdict()
            testcases.append(testcase)
        return testcases
