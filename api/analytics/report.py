#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/2/10 21:13
# author: fengqiyuan
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from common.logger import logger
from models.analytics.report import Report
from blueprints import report_bp
from services.account.role_service import check_permission, check_project_permission, get_project_role_project_ids
from services.analytics.report_service import ReportService
from services.analytics.result_service import ResultService


@report_bp.route('/<int:report_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_report', scope='project')
def delete_report(report_id):
    try:
        report = Report.get_report(report_id)
        if not report:
            return jsonify(errcode=1, message="无有效数据")
        user = get_jwt_identity()
        user_id = user.get('user_id')
        project_id = report.get('project_id')
        if not check_project_permission(user_id, project_id, 'delete_report'):
            return jsonify(errcode=1, message="无权限")
        Report.delete_report(report_id)
        return jsonify(errcode=0, message="删除成功")
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=1, message="删除失败")


@report_bp.route('/<int:report_id>', methods=['GET'])
@jwt_required()
@check_permission('get_reports', scope='project')
def get_report(report_id):
    report = ReportService.get_report(report_id)
    if not report:
        return jsonify(errcode=1, message="无有效数据")
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_id = report.get('project_id')
    if not check_project_permission(user_id, project_id, 'get_reports'):
        return jsonify(errcode=1, message="无权限")
    results = ResultService.get_result(report_id)
    report['results'] = results
    return jsonify(errcode=0, data=report)


@report_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_reports', scope='project')
def get_reports():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_reports')
    reports, total, page_total, iter_pages = ReportService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, message="查询成功", data=reports, total=total, page_total=page_total,
                   iter_pages=iter_pages)


