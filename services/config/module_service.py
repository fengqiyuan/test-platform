#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:30
# author: fengqiyuan
from sqlalchemy import select
from sqlalchemy.orm import aliased, Bundle

from models.account.user import User
from models.config.module import Module, db
from models.config.project import Project


class ModuleService:

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("module", Module.module_id, Module.module_code, Module.module_name, Module.description,
                        Module.parent_module_id, Module.project_id, Project.project_name,
                        Module.creator, Module.updater, Module.create_time, Module.update_time,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username'))
        query = select(bundle).join_from(Module, Project, Module.project_id == Project.project_id) \
            .join(creator, creator.user_id == Module.creator) \
            .join(updater, updater.user_id == Module.updater) \
            .where(Module.status == True, Project.project_id.in_(project_ids))
        results = db.paginate(query, page=page_no, per_page=page_size)
        modules, total, page_total, iter_pages = [], 0, 0, []
        if results:
            modules = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return modules, total, page_total, iter_pages
