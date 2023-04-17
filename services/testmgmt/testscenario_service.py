#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 09:45
# author: fengqiyuan
from sqlalchemy import select
from sqlalchemy.orm import aliased, Bundle

from models.account.user import User
from models.config.module import Module
from models.config.project import Project
from models.testmgmt.testscenario import TestScenario, db


class TestScenarioService:

    @staticmethod
    def get_scenario(scenario_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("scenario", TestScenario.scenario_id, TestScenario.scenario_code,
                        TestScenario.scenario_name, TestScenario.scenario_level, TestScenario.scenario_type,
                        TestScenario.project_id, Project.project_name, TestScenario.module_id,
                        Module.module_name, TestScenario.description, TestScenario.create_time,
                        TestScenario.update_time, TestScenario.creator, TestScenario.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(TestScenario, Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Module, Module.module_id == TestScenario.module_id) \
            .outerjoin(creator, creator.user_id == TestScenario.creator) \
            .outerjoin(updater, updater.user_id == TestScenario.updater) \
            .where(TestScenario.status == True, TestScenario.scenario_id == scenario_id)

        result = db.session.execute(query).scalars().first()
        scenario = result._asdict() if result else {}
        return scenario

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("scenario", TestScenario.scenario_id, TestScenario.scenario_code,
                        TestScenario.scenario_name, TestScenario.scenario_level, TestScenario.scenario_type,
                        TestScenario.project_id, Project.project_name, TestScenario.module_id,
                        Module.module_name, TestScenario.description, TestScenario.create_time,
                        TestScenario.update_time, TestScenario.creator, TestScenario.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(TestScenario, Project, Project.project_id == TestScenario.project_id) \
            .outerjoin(Module, Module.module_id == TestScenario.module_id) \
            .outerjoin(creator, creator.user_id == TestScenario.creator) \
            .outerjoin(updater, updater.user_id == TestScenario.updater) \
            .where(TestScenario.status == True, Project.project_id.in_(project_ids)
                   ).order_by(TestScenario.scenario_id.desc())

        results = db.paginate(query, page=page_no, per_page=page_size)
        scenarios, total, page_total, iter_pages = [], 0, 0, []
        if results:
            scenarios = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return scenarios, total, page_total, iter_pages
