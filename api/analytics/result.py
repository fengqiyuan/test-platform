#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/26 08:28
# author: fengqiyuan
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from blueprints import result_bp
from services.account.role_service import check_permission, check_project_permission, get_project_role_project_ids
from services.analytics.result_service import ResultService


@result_bp.route('/<int:result_id>', methods=['GET'])
@jwt_required()
@check_permission('get_results', scope='project')
def get_result(result_id):
    result = ResultService.get_result(result_id)
    if not result:
        return jsonify(errcode=1, message="无有效数据")
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_id = result.get('project_id')
    if not check_project_permission(user_id, project_id, 'get_results'):
        return jsonify(errcode=1, message="无权限")
    return jsonify(errcode=0, data=result)


@result_bp.route('', methods=['GET'])
@jwt_required()
@check_permission('get_results', scope='project')
def get_results():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_results')
    results, total, page_total, iter_pages = ResultService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, message="查询成功", data=results, total=total, page_total=page_total,
                   iter_pages=iter_pages)
