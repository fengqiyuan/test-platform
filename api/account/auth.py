#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 10:55
# author: fengqiyuan
from datetime import datetime
import json
import random

from flask import request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt, create_refresh_token
from flask_mail import Message
from sqlalchemy import select, insert, update

from common.validate import is_valid_datetime
from exts import db, mail, cache, jwt
from models.account.user import User
from blueprints import auth_bp
from common.logger import logger


@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    token_in_redis = cache.get(jti)
    return token_in_redis is not None


@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        user = request.json
        if not isinstance(user, dict):
            return jsonify(errcode=1, message='数据类型不正确')
        username = user.get('username')
        password = user.get('password')
        email = user.get('email')
        join_time = user.get('join_time', datetime.now())
        avatar = user.get('avatar')
        if not username or not password or not email:
            return jsonify(errcode=1, message='缺少必填字段')
        if not isinstance(username, str) or not isinstance(password, str) or not isinstance(email, str) or \
                not isinstance(join_time, (str, datetime)) or not isinstance(avatar, (str, type(None))):
            return jsonify(errcode=1, message='字段类型不正确')
        if isinstance(join_time, str) and not is_valid_datetime(join_time):
            return jsonify(errcode=1, message='join_time格式不正确')
        password_hash, salt = User.generate_password_hash(password)
        insert_dict = {
            'username': username,
            'password_hash': password_hash,
            'salt': salt,
            'email': email,
            'join_time': join_time,
            'avatar': avatar
        }
        stmt = insert(User).values(**insert_dict)
        result = db.session.execute(stmt)
        update_stmt = update(User).where(User.user_id == result.inserted_primary_key[0]
                                         ).values(creator=result.inserted_primary_key[0],
                                                  create_time=datetime.now(),
                                                  updater=result.inserted_primary_key[0],
                                                  update_time=datetime.now())
        db.session.execute(update_stmt)
        db.session.commit()
        return jsonify(errcode=0, message='success')
    except Exception as e:
        db.session.rollback()
        logger.error(str(e))
        return jsonify(errcode=1, message='数据库报错', error=str(e)), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data.decode('utf-8')) if request.data else {} or request.args or request.form
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify(errcode=1, message="username and password are required")
    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify(errcode=1, message="Invalid username or password")
    user = User.check_login_user(username, password)
    if not user:
        return jsonify(errcode=1, message="Invalid username or password")
    # 生成用户相关的token
    access_token = create_access_token(identity=user)
    refresh_token = create_refresh_token(identity=user)
    user['access_token'] = access_token
    user['refresh_token'] = refresh_token
    logger.info(user)
    res = jsonify(errcode=0, message="Login successful", data=user)
    return res


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        jti = get_jwt()["jti"]
        cache.set(jti, "", timeout=int(current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()))
        return jsonify(errcode=0, message="logout successful")
    except Exception as e:
        logger.error(e)
        return jsonify(errcode=0, message="logout successful")


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)
    return jsonify(access_token=access_token, refresh_token=refresh_token)


@auth_bp.route('/user', methods=['GET'])
@jwt_required()
def get_login_user():
    user = get_jwt_identity()
    return jsonify(errcode=0, data=user)


@auth_bp.route('/email/captcha')
def mail_captcha():
    email = request.args.get("email")
    digits = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    captcha = "".join(random.sample(digits, 6))
    body = f'您的注册验证码是：{captcha}，请勿告诉别人！'
    message = Message(subject="注册验证码", recipients=[email], body=body)
    cache.set(email, captcha, timeout=3000)
    mail.send(message)
    return jsonify(errcode=0, message="success")
