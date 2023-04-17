#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/27 00:33
# author: fengqiyuan
from flask import jsonify
from flask_jwt_extended import jwt_required

from blueprints import statistics_bp
from services.analytics.statistics_service import StatisticsService


@statistics_bp.route('', methods=['GET'])
@jwt_required()
def get_statistics():
    result = StatisticsService.get_result_statistics()
    testsuite = StatisticsService.get_testsuite_statistics()
    testscenario = StatisticsService.get_testscenario_statistics()
    testcase = StatisticsService.get_testcase_statistics()
    return jsonify(errcode=0, result=result, testsuite=testsuite, testscenario=testscenario, testcase=testcase)

