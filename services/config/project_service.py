#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:31
# author: fengqiyuan
from datetime import datetime

import pytz
from sqlalchemy import select
from sqlalchemy.orm import aliased, Bundle

from models.account.user import User
from models.config.project import Project, db


class ProjectService:

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        # 获取当前时区
        local_tz = datetime.now().astimezone().tzinfo
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("project", Project.project_id, Project.project_code, Project.project_name, Project.git_url,
                        Project.description, Project.creator, Project.updater,
                        Project.create_time,
                        Project.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username'))

        query = select(bundle).select_from(Project) \
            .join(creator, creator.user_id == Project.creator) \
            .join(updater, updater.user_id == Project.updater) \
            .where(Project.status == True, Project.project_id.in_(project_ids))
        results = db.paginate(query, page=page_no, per_page=page_size)
        projects, total, page_total, iter_pages = [], 0, 0, []
        if results:
            projects = [item._asdict() for item in results.items]
            print(projects[0]['create_time'])
            print(type(projects[0]['create_time']))
            print(projects[0]['update_time'])
            print(type(projects[0]['update_time']))
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return projects, total, page_total, iter_pages
