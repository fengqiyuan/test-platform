#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/1 07:42
# author: fengqiyuan
import json
from dataclasses import asdict
from flask import jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import insert, update, select
from models.tools.mock import Mock, db
from blueprints import mock_bp
from services.account.role_service import check_permission, get_project_role_project_ids, check_model_permission
from services.tools.mock_service import MockService


@mock_bp.route('<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def mock_handler(path):
    # 1.先根据path和方法查询数据
    path = request.path.replace('/tools', '')
    results = db.session.execute(select(Mock).where(
        Mock.path == path, Mock.method == request.method)).scalars()
    mock_datas = [asdict(result) for result in results]
    if mock_datas:
        # 2.根据 headers, params, body 筛选数据
        # 2.1处理params参数, 转成dict
        params = dict(request.args)
        # 2.2处理header参数，只需要check指定数据
        headers = dict(request.headers)
        # 2.3需要需要check的指定header key
        header_keys = ['Content-Type', 'Authorization', 'Cookie', 'token']
        check_headers = {}
        for key in header_keys:
            if headers.get(key):
                check_headers.update({key: headers.get(key)})
        # 2.4处理body
        try:
            data = json.loads(request.data.decode('utf-8'))
        except ValueError as e:
            print("该字符串不能转成JSON对象:", e)
            if request.data:
                data = request.data.decode('utf-8')
            elif request.form:
                data = dict(request.form)
            else:
                data = ''
        # 2.5 处理请求URL
        original_host = request.headers.get('X-Forwarded-Host')
        original_url = ''
        if original_host:
            # Mock不走代理, 直接请求Mock服务, 无法区分环境
            # 走Mock代理，可以区分环境, 这是走代理的处理逻辑
            original_proto = request.headers.get('X-Forwarded-Proto', request.scheme)
            original_url = f"{original_proto}://{original_host}{path}"
        # 3 筛选数据
        result = {}
        for mock_data in mock_datas:
            # 3.1 根据URL筛选数据
            if original_url and original_url != data['url']:
                continue
            if data['headers'] and check_headers != json.loads(data['headers']) or \
                    len(data['headers']) == 0 and len(check_headers) != 0:
                continue
            if data['params'] and params != json.loads(data['params']) or \
                    len(data['params']) == 0 and len(params) != 0:
                continue
            if type(data) == 'dict' and data['body'] and data != json.loads(data['body']) or \
                    len(data['body']) == 0 and len(data) != 0 or data != data['body']:
                continue
            result = mock_data
            break
        # 4 处理请求
        if result and result['response_type'] == 'JSON':
            return json.loads(result['response_data']), result['response_status'], json.loads(
                result['response_headers'])
        elif result:
            return ['response_data'], result['response_status'], json.loads(result['response_headers'])
        else:
            return jsonify(errno=1, message="找不到params相同、headers相同和body相同的Mock数据"), 404

    else:
        return jsonify(errno=1, message="找不到路径相同、方法相同的Mock数据"), 404


@mock_bp.route('/mock-data', methods=['POST'])
@jwt_required()
@check_permission('create_mock_data', scope='project')
def create_mock_data():
    data = request.json if request.data else {}
    mock_name = data.get('mock_name', '')
    project_id = data.get('project_id', 0)
    module_id = data.get('module_id', 0)
    url = data.get('url', '')
    path = data.get('path', '')
    method = data.get('method', '')
    response_status = data.get('response_status', '')
    response_data = data.get('response_data', '')
    if data and mock_name and project_id and module_id and url and path and method and response_status \
            and response_data:
        params = json.dumps(data['params']) if data.get('params', None) else ''
        headers = json.dumps(data['headers']) if data.get('headers', None) else ''
        raw_data = json.dumps(data['data']) if data.get('data', None) else ''
        response_headers = json.dumps(data['response_headers']) if data.get('response_headers', None) else ''
        insert_dict = {
            'mock_code': data.get('mock_code', ''),
            'mock_name': mock_name,
            'project_id': project_id,
            'module_id': module_id,
            'env_id': data.get('env_id', ''),
            'url': url,
            'path': path,
            'method': method,
            'params': params,
            'headers': headers,
            'data': raw_data,
            'response_headers': response_headers,
            'response_data': response_data,
            'response_status': response_status
        }
        try:
            stmt = insert(Mock).values(**insert_dict)
            db.session.execute(stmt)
            db.session.commit()
            mock_id = db.session.execute(select(Mock.mock_id).where(Mock.mock_name == mock_name)
                                         .where(Mock.status == True)).scalars().first()
            return jsonify(errcode=0, message='success', mock_id=mock_id)
        except Exception as e:
            db.session.rollback()
            return jsonify(errcode=1, message='数据库报错', error=str(e)), 500
    else:
        return jsonify(errcode=1, message='缺少必填字段'), 400


@mock_bp.route('/mock-data/<int:id>', methods=['PUT'])
@jwt_required()
@check_permission('update_mock_data', scope='project')
def update_mock_data(id):
    data = request.json if request.data else {}
    mock_name = data.get('mock_name', '')
    project_id = data.get('project_id', 0)
    module_id = data.get('module_id', 0)
    url = data.get('url', '')
    path = data.get('path', '')
    method = data.get('method', '')
    response_status = data.get('response_status', '')
    response_data = data.get('response_data', '')
    if data and mock_name and project_id and module_id and url and path and method and response_status \
            and response_data:
        params = json.dumps(data['params']) if data.get('params', None) else ''
        headers = json.dumps(data['headers']) if data.get('headers', None) else ''
        raw_data = json.dumps(data['data']) if data.get('data', None) else ''
        response_headers = json.dumps(data['response_headers']) if data.get('response_headers', None) else ''
        update_dict = {
            'mock_code': data.get('mock_code', ''),
            'mock_name': mock_name,
            'project_id': project_id,
            'module_id': module_id,
            'env_id': data.get('env_id', ''),
            'url': url,
            'path': path,
            'method': method,
            'params': params,
            'headers': headers,
            'data': raw_data,
            'response_headers': response_headers,
            'response_data': response_data,
            'response_status': response_status
        }
        try:
            stmt = update(Mock).where(Mock.mock_id == id).values(**update_dict)
            db.session.execute(stmt)
            db.session.commit()
            return jsonify(errcode=0, message='success')
        except Exception as e:
            db.session.rollback()
            return jsonify(errcode=1, message='数据库报错', error=str(e)), 500
    else:
        return jsonify(errcode=1, message='缺少必填字段'), 400


@mock_bp.route('/mock-data/<int:mock_id>', methods=['DELETE'])
@jwt_required()
@check_permission('delete_mock_data', scope='project')
def delete_mock_data(mock_id):
    try:
        user = get_jwt_identity()
        user_id = user.get('user_id')
        if not check_model_permission(user_id, Mock, mock_id, 'get_mock_apis'):
            return jsonify(errcode=1, message="无权限")
        mock_data = db.session.execute(select(Mock).where(Mock.mock_id == mock_id)).scalars().first()
        mock_data.status = False
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        return jsonify(errcode=1, message='数据库报错', error=str(e)), 500


@mock_bp.route('/mock-data/<int:mock_id>', methods=['GET'])
@jwt_required()
@check_permission('get_mock_apis', scope='project')
def get_mock_api(mock_id):
    user = get_jwt_identity()
    user_id = user.get('user_id')
    if not check_model_permission(user_id, Mock, mock_id, 'get_mock_apis'):
        return jsonify(errcode=1, message="无权限")
    result = MockService.get_mock_data(mock_id)
    return jsonify(errcode=0, data=result)


@mock_bp.route('/mock-data', methods=['GET'])
@jwt_required()
@check_permission('get_mock_apis', scope='project')
def get_mock_apis():
    page_no = request.args.get("pageNo", 1, int)
    page_size = current_app.config['PER_PAGE_COUNT']
    user = get_jwt_identity()
    user_id = user.get('user_id')
    project_ids = get_project_role_project_ids(user_id, 'get_mock_apis')
    mock_apis, total, page_total, iter_pages = MockService.paginate(page_no, page_size, project_ids)
    return jsonify(errcode=0, data=mock_apis, total=total, page_total=page_total, iter_pages=iter_pages)
