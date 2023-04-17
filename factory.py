#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/12 17:18
# author: fengqiyuan
import json
from datetime import datetime
from decimal import Decimal
import pytz
from flask import Flask

from config import config
from exts import db, mail, cache, jwt, migrate, cors
from api.account.auth import auth_bp
from api.account.role import role_bp
from api.account.user import user_bp
from api.analytics.report import report_bp
from api.analytics.result import result_bp
from api.analytics.statistics import statistics_bp
from api.automation.execution import execution_bp
from api.automation.runner import runner_bp
from api.automation.schedule import schedule_bp
from api.config.environment import env_bp
from api.config.module import module_bp
from api.config.project import project_bp
from api.testmgmt.testcase import testcase_bp
from api.testmgmt.testscenario import scenario_bp
from api.testmgmt.testsuite import testsuite_bp
from api.tools.mock import mock_bp


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.astimezone(pytz.timezone('UTC')).strftime('%a, %d %b %Y %H:%M:%S %Z')
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def create_app(config_name):
    app = Flask(__name__)
    # 读取配置
    app.config.from_object(config[config_name])
    # app.config['JSON_SORT_KEYS'] = False
    app.json_encoder = CustomJSONEncoder

    # 初始化扩展
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)

    # 注册蓝图
    app.register_blueprint(auth_bp)
    app.register_blueprint(role_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(statistics_bp)
    app.register_blueprint(execution_bp)
    app.register_blueprint(runner_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(env_bp)
    app.register_blueprint(module_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(testcase_bp)
    app.register_blueprint(scenario_bp)
    app.register_blueprint(testsuite_bp)
    app.register_blueprint(mock_bp)

    # 初始化 Flask-JWT-Extended
    jwt.init_app(app)
    # 初始化 CORS
    cors.init_app(app)

    return app
