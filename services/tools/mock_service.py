#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:11
# author: fengqiyuan
from sqlalchemy import select
from sqlalchemy.orm import Bundle

from models.account.user import User
from models.config.environment import Environment
from models.config.module import Module
from models.config.project import Project
from models.tools.mock import Mock, db


class MockService:

    @staticmethod
    def get_mock_data(mock_id):
        creator = db.aliased(User)
        updater = db.aliased(User)
        bundle = Bundle("tools", Mock.mock_id, Mock.mock_code, Mock.mock_name, Mock.project_id,
                        Project.project_name, Mock.module_id, Module.module_name, Mock.env_id,
                        Environment.env_name, Environment.env_url, Mock.url, Mock.path, Mock.method, Mock.params,
                        Mock.headers, Mock.data, Mock.response_status, Mock.response_headers,
                        Mock.response_data, Mock.creator, Mock.updater, Mock.create_time, Mock.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Mock, Project, Project.project_id == Mock.project_id) \
            .outerjoin(Module, Module.module_id == Mock.module_id) \
            .join(Environment, Environment.env_id == Mock.env_id) \
            .join(creator, creator.user_id == Mock.creator) \
            .outerjoin(updater, updater.user_id == Mock.updater) \
            .where(Mock.mock_id == mock_id)

        result = db.session.execute(query).scalars().first()
        return result._asdict() if result else {}

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = db.aliased(User)
        updater = db.aliased(User)
        bundle = Bundle("tools", Mock.mock_id, Mock.mock_code, Mock.mock_name, Mock.project_id,
                        Project.project_name, Mock.module_id, Module.module_name, Mock.env_id,
                        Environment.env_name, Environment.env_url, Mock.url, Mock.path, Mock.method, Mock.params,
                        Mock.headers, Mock.data, Mock.response_status, Mock.response_headers,
                        Mock.response_data, Mock.creator, Mock.updater, Mock.create_time, Mock.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )

        query = select(bundle).join_from(Mock, Project, Project.project_id == Mock.project_id) \
            .outerjoin(Module, Module.module_id == Mock.module_id) \
            .join(Environment, Environment.env_id == Mock.env_id) \
            .join(creator, creator.user_id == Mock.creator) \
            .join(updater, updater.user_id == Mock.updater) \
            .where(Mock.status == True, Project.project_id.in_(project_ids)).order_by(Mock.mock_id.desc())
        results = db.paginate(query, page=page_no, per_page=page_size)
        mock_datas, total, page_total, iter_pages = [], 0, 0, []
        if results:
            mock_datas = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return mock_datas, total, page_total, iter_pages
