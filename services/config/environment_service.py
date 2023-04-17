#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:30
# author: fengqiyuan
from sqlalchemy import select, String
from sqlalchemy.orm import aliased, Bundle

from models.account.user import User
from models.config.environment import Environment, db
from models.config.project import Project


class EnvironmentService:

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("env", Environment.env_id, Environment.env_name, Environment.protocol,
                        Environment.hostname, Environment.port, Environment.env_url, Environment.db_config.cast(String),
                        Environment.redis_config.cast(String), Environment.description,
                        Environment.project_id, Project.project_name, Environment.creator, Environment.updater,
                        Environment.create_time, Environment.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username'))

        query = select(bundle).join_from(Environment, Project, Project.project_id == Environment.project_id) \
            .join(creator, creator.user_id == Environment.creator) \
            .join(updater, updater.user_id == Environment.updater) \
            .where(Environment.status == True, Project.project_id.in_(project_ids))
        results = db.paginate(query, page=page_no, per_page=page_size)
        environments, total, page_total, iter_pages = [], 0, 0, []
        if results:
            environments = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return environments, total, page_total, iter_pages
