#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/12 16:51
# author: fengqiyuan
from flask import Blueprint

# account目录
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
role_bp = Blueprint("role", __name__, url_prefix='/roles')
user_bp = Blueprint("user", __name__, url_prefix='/users')

# analytics目录
report_bp = Blueprint("report", __name__, url_prefix='/reports')
result_bp = Blueprint("result", __name__, url_prefix='/results')
statistics_bp = Blueprint("statistics", __name__, url_prefix='/statistics')

# automation目录
execution_bp = Blueprint("execution", __name__, url_prefix='/executions')
runner_bp = Blueprint("runner", __name__, url_prefix='/runners')
schedule_bp = Blueprint("schedule", __name__, url_prefix='/schedules')

# config目录
env_bp = Blueprint("environment", __name__, url_prefix='/environments')
module_bp = Blueprint("module", __name__, url_prefix='/modules')
project_bp = Blueprint("project", __name__, url_prefix='/projects')

# testmgmt目录
scenario_bp = Blueprint("scenario", __name__, url_prefix='/scenarios')
testcase_bp = Blueprint("testcase", __name__, url_prefix='/testcases')
testsuite_bp = Blueprint("suite", __name__, url_prefix='/testsuites')

# tools目录
mock_bp = Blueprint("mock", __name__, url_prefix="/mocks")





