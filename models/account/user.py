#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/11/7 09:49
# author: fengqiyuan
import os
import scrypt
from datetime import datetime
from sqlalchemy import func, select, Column, Integer, String, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship, aliased, Bundle

from exts import db
from models.account.user_role import UserProjectRole


class User(db.Model):
    user_id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(1000), nullable=False)
    salt = Column(String(1000), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    join_time = Column(TIMESTAMP, default=datetime.now)
    avatar = Column(String(200))
    create_time = Column(TIMESTAMP, default=datetime.now)
    update_time = Column(TIMESTAMP, default=datetime.now, onupdate=datetime.now)
    creator = Column(Integer)
    updater = Column(Integer)
    status = Column(Boolean, default=True)
    projects = relationship('Project', secondary=UserProjectRole.__table__, back_populates='users')

    @property
    def password(self):
        raise AttributeError('password is not readable!')

    @staticmethod
    def generate_password_hash(password):
        # generate a random salt
        salt = os.urandom(16)
        password_hash = scrypt.hash(password, salt)
        return password_hash.decode('iso-8859-1'), salt.decode('iso-8859-1')

    @staticmethod
    def check_password_hash(password, salt, password_hash):
        check_password_hash = scrypt.hash(password, salt=salt)
        return check_password_hash == password_hash

    @staticmethod
    def check_login_user(username, password):
        result = db.session.execute(
            select(User.salt, User.password_hash, User.user_id, User.username
                   ).where(User.username == username, User.status == True)).first()
        if result:
            salt, password_hash, user_id, username = result
            if User.check_password_hash(password, salt.encode('iso-8859-1'), password_hash.encode('iso-8859-1')):
                return {'user_id': user_id, 'username': username}
        return {}

    @staticmethod
    def search_users(query):
        results = db.session.execute(select(User.user_id, User.username)
                                     .where(User.status == True, User.username.like('%%{}%%'.format(query)))).all()
        return [result._asdict() for result in results]

    @staticmethod
    def paginate(page_no, page_size):
        creator = aliased(User)
        updater = aliased(User)
        bundle = Bundle("User", User.user_id, User.username, User.email, User.join_time, User.avatar, User.create_time,
                        User.update_time, User.creator, User.updater,
                        creator.username.label('creator_username'),
                        updater.username.label('updater_username')
                        )
        query = select(bundle).select_from(User) \
            .outerjoin(creator, creator.user_id == User.creator) \
            .outerjoin(updater, updater.user_id == User.updater) \
            .where(User.status == True)

        results = db.paginate(query, page=page_no, per_page=page_size)
        scenarios, total, page_total, iter_pages = [], 0, 0, []
        if results:
            scenarios = [item._asdict() for item in results.items]
            total = results.total
            page_total = results.pages
            iter_pages = list(results.iter_pages())
        return scenarios, total, page_total, iter_pages

