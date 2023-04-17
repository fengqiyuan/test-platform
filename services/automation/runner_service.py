#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:31
# author: fengqiyuan
from sqlalchemy import select, insert, update
from sqlalchemy.orm import aliased, Bundle

from common.logger import logger
from models.account.user import User
from models.automation.runner import Runner, db, RunnerTestSuite
from models.config.environment import Environment
from models.config.project import Project
from models.testmgmt.testsuite import TestSuite


class RunnerService:

    @staticmethod
    def create_runner(runner_dict, testsuites_list, creator):
        try:
            result = db.session.execute(insert(Runner).values(creator=creator, updater=creator, **runner_dict))
            runner_id = result.inserted_primary_key[0]
            db.session.execute(insert(RunnerTestSuite).values(runner_id=runner_id, creator=creator, updater=creator),
                               testsuites_list)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def update_runner(runner_id, runner_dict, testsuite_ids, testsuites_list, updater):
        try:
            db.session.execute(update(Runner).where(Runner.runner_id == runner_id).values(updater=updater),
                               runner_dict)
            pre_testsuite_ids = db.session.execute(
                select(RunnerTestSuite.testsuite_id).where(RunnerTestSuite.runner_id == runner_id,
                                                           RunnerTestSuite.status == True)
            ).scalars().all()
            delete_testsuite_ids = list(set(pre_testsuite_ids) - set(testsuite_ids))
            update_testsuite_ids = list(set(pre_testsuite_ids) & set(testsuite_ids))  # 不做处理
            insert_testsuite_ids = list(set(testsuite_ids) - set(pre_testsuite_ids))
            # 无效删除的数据
            if delete_testsuite_ids:
                update_stmt = update(RunnerTestSuite).where(
                    RunnerTestSuite.runner_id == runner_id, RunnerTestSuite.status == True,
                    RunnerTestSuite.testsuite_id.in_(delete_testsuite_ids)
                ).values(status=False, updater=updater)
                db.session.execute(update_stmt)
            if insert_testsuite_ids:
                insert_stmt = insert(RunnerTestSuite).where(
                    RunnerTestSuite.runner_id == runner_id, RunnerTestSuite.status == True,
                ).values(updater=updater)
                db.session.execute(insert_stmt, testsuites_list)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise

    @staticmethod
    def get_runner(runner_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("runner", Runner.runner_id, Runner.runner_name, Runner.description,
                        Runner.project_id, Project.project_name, Runner.env_id, Environment.env_name,
                        Environment.env_url, Runner.create_time, Runner.update_time,
                        Runner.creator, Runner.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Runner, Project, Project.project_id == Runner.project_id) \
            .join(Environment, Environment.env_id == Runner.env_id) \
            .outerjoin(creator, creator.user_id == Runner.creator) \
            .outerjoin(updater, updater.user_id == Runner.updater) \
            .where(Runner.runner_id == runner_id, Runner.status == True)

        result = db.session.execute(query).scalar()
        return result._asdict() if result else {}

    @staticmethod
    def get_runner_testsuites(runner_id):
        bundle = Bundle("RunnerTestSuite", RunnerTestSuite.testsuite_id, TestSuite.testsuite_name, Project.project_id,
                        Project.project_name, TestSuite.total, TestSuite.single_total
                        )
        query = select(bundle).join_from(RunnerTestSuite, TestSuite,
                                         RunnerTestSuite.testsuite_id == TestSuite.testsuite_id) \
            .join(Project, TestSuite.project_id == Project.project_id) \
            .where(RunnerTestSuite.runner_id == runner_id, RunnerTestSuite.status == True)

        results = db.session.execute(query).scalars()
        testsuites = []
        for result in results:
            testsuites.append(result._asdict())
        return testsuites

    @staticmethod
    def get_execute_runner(runner_id):
        bundle = Bundle("runner", Runner.runner_id, Runner.runner_name, Runner.project_id, Runner.env_id,
                        Environment.env_url)
        query = select(bundle).join_from(Runner, Project, Project.project_id == Runner.project_id) \
            .join(Environment, Environment.env_id == Runner.env_id) \
            .where(Runner.runner_id == runner_id, Runner.status == True)

        result = db.session.execute(query).scalar()
        return result._asdict() if result else {}

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("runner", Runner.runner_id, Runner.runner_name, Runner.description,
                        Runner.project_id, Project.project_name, Runner.env_id, Environment.env_name,
                        Environment.env_url, Runner.create_time, Runner.update_time,
                        Runner.creator, Runner.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Runner, Project, Project.project_id == Runner.project_id) \
            .join(Environment, Environment.env_id == Runner.env_id) \
            .outerjoin(creator, creator.user_id == Runner.creator) \
            .outerjoin(updater, updater.user_id == Runner.updater) \
            .where(Runner.status == True, Project.project_id.in_(project_ids)).order_by(Runner.runner_id.desc())

        results = db.paginate(query, page=page_no, per_page=page_size)
        runners, total, page_total, iter_pages = [], 0, 0, []
        if results:
            runners = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return runners, total, page_total, iter_pages
