#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/28 10:32
# author: fengqiyuan
from sqlalchemy import select
from sqlalchemy.orm import aliased, Bundle

from models.account.user import User
from models.automation.runner import Runner
from models.automation.schedule import Schedule, db
from models.config.project import Project


class ScheduleService:

    @staticmethod
    def get_schedule(schedule_id):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("schedule", Schedule.schedule_id, Schedule.schedule_name, Schedule.project_id,
                        Project.project_name, Schedule.runner_id, Runner.runner_name, Schedule.cron,
                        Schedule.execute_time, Schedule.execute_status, Schedule.description, Schedule.create_time,
                        Schedule.update_time, Schedule.creator, Schedule.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Schedule, Project, Project.project_id == Schedule.project_id) \
            .join(Runner, Runner.runner_id == Schedule.runner_id) \
            .outerjoin(creator, creator.user_id == Schedule.creator) \
            .outerjoin(updater, updater.user_id == Schedule.updater) \
            .where(Schedule.schedule_id == schedule_id, Schedule.status == True)

        result = db.session.execute(query).scalars().first()
        return result._asdict()

    @staticmethod
    def get_execute_schedules():
        bundle = Bundle("Schedule", Schedule.schedule_id, Schedule.runner_id, Schedule.cron)
        query = select(bundle).select_from(Schedule).where(Schedule.status == True)

        results = db.session.execute(query).scalars()
        return results

    @staticmethod
    def paginate(page_no, page_size, project_ids):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("schedule", Schedule.schedule_id, Schedule.schedule_name, Schedule.project_id,
                        Project.project_name, Schedule.runner_id, Runner.runner_name, Schedule.cron,
                        Schedule.execute_time, Schedule.execute_status, Schedule.description, Schedule.create_time,
                        Schedule.update_time, Schedule.creator, Schedule.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).join_from(Schedule, Project, Project.project_id == Schedule.project_id) \
            .join(Runner, Runner.runner_id == Schedule.runner_id) \
            .outerjoin(creator, creator.user_id == Schedule.creator) \
            .outerjoin(updater, updater.user_id == Schedule.updater) \
            .where(Schedule.status == True, Project.project_id.in_(project_ids)).order_by(Schedule.schedule_id.desc())

        results = db.paginate(query, page=page_no, per_page=page_size)
        schedules, total, page_total, iter_pages = [], 0, 0, []
        if results:
            schedules = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return schedules, total, page_total, iter_pages
