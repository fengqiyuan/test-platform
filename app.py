#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/10/7 22:12
# author: fengqiyuan
import os
from datetime import datetime, timedelta

import croniter as croniter
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import factory
from common.logger import logger
from config import config
from models.config.environment import Environment
from services.automation.execution_service import ExecutionService
from services.automation.runner_service import RunnerService
from services.automation.schedule_service import ScheduleService

app = factory.create_app(os.getenv('FLASK_ENV') or 'default')

# 获取当前时区
local_tz = datetime.now().astimezone().tzinfo
# apscheduler配置
scheduler = BackgroundScheduler()
jobstores = {
    'mysql': {'type': 'sqlalchemy', 'url': config[os.getenv('FLASK_ENV') or 'default'].SQLALCHEMY_DATABASE_URI},
    'default': SQLAlchemyJobStore(url=config[os.getenv('FLASK_ENV') or 'default'].SQLALCHEMY_DATABASE_URI)
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=local_tz)


@scheduler.scheduled_job('cron', second=5, id="job")
def exec_job():
    """执行定时任务"""
    with app.app_context():
        try:
            now = datetime.now(local_tz)
            schedules = ScheduleService.get_execute_schedules()
            for schedule in schedules:
                schedule_id = schedule[0]
                runner_id = schedule[1]
                cron = schedule[2]
                start_time = now - timedelta(minutes=1)
                cron = croniter.croniter(cron, start_time)
                next_time = datetime.fromtimestamp(cron.get_next(start_time=start_time), local_tz)
                if next_time <= now:
                    logger.info(f"定时任务{schedule_id}执行Runner{runner_id}执行开始于{now}")
                    runner = RunnerService.get_execute_runner(runner_id)
                    env = Environment.get_environment(runner.get('env_id'))
                    execute = ExecutionService(env, runner=runner)
                    execute.execute_runner()
                    logger.info(f"定时任务{schedule_id}执行Runner{runner_id}执行结束于{datetime.now(local_tz)}")
        except Exception as e:
            logger.error(f"Error executing scheduled job: {e}")


# 启动调度器
scheduler.start()


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/health-check')
def health_check():
    return 'ok'


@app.route('/job')
def index():
    exec_job()
    return "execute job"


if __name__ == '__main__':
    app.run()
