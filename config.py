#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/10/7 22:12
# author: fengqiyuan
import os
import datetime
from jenkinsapi.jenkins import Jenkins

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    # Flask-WTF密钥配置 目前没用到
    SECRET_KEY = "woqrewqorewrwer"
    # 分页数量
    PER_PAGE_COUNT = 10
    # 邮件配置
    MAIL_SERVER = "smtp.qq.com"
    MAIL_USE_SSL = True
    MAIL_PORT = 465
    MAIL_USERNAME = "username@mail.com"
    MAIL_PASSWORD = "authorization"
    MAIL_DEFAULT_SENDER = "username@mail.com"


class DevelopmentConfig(BaseConfig):
    # sqlalchemy配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@192.168.31.143:3306/test_platform?charset=utf8mb4"
    # redis配置
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "192.168.31.143"
    CACHE_REDIS_PORT = "6379"
    # CACHE_REDIS_PASSWORD = "123456"
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300
    # Jenkins配置
    # jenkins = Jenkins('http://192.168.31.143:8080/', useCrumb=True, username='fengqiyuan', password='fengqiyuan')
    # JWT配置
    JWT_SECRET_KEY = 'testtest'
    # JWT_TOKEN_LOCATION = ['headers', 'cookies', 'json', 'query_string'] # 默认headers
    JWT_TOKEN_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)


class TestConfig(BaseConfig):
    # sqlalchemy配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@192.168.31.143:3306/test_platform?charset=utf8mb4"
    # redis配置
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "192.168.31.143"
    CACHE_REDIS_PORT = "6379"
    # CACHE_REDIS_PASSWORD = "123456"
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300
    # Jenkins配置
    # jenkins = Jenkins('http://192.168.31.143:8080/', useCrumb=True, username='fengqiyuan', password='fengqiyuan')
    # JWT配置
    JWT_SECRET_KEY = 'testtest'
    # JWT_TOKEN_LOCATION = ['headers', 'cookies', 'json', 'query_string'] # 默认headers
    JWT_TOKEN_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)


class ProductionConfig(BaseConfig):
    # sqlalchemy配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123456@192.168.31.143:3306/test_platform?charset=utf8mb4"
    # redis配置
    CACHE_TYPE = "RedisCache"
    CACHE_REDIS_HOST = "192.168.31.143"
    CACHE_REDIS_PORT = "6379"
    # CACHE_REDIS_PASSWORD = "123456"
    CACHE_REDIS_DB = 0
    CACHE_DEFAULT_TIMEOUT = 300
    # Jenkins配置
    # jenkins = Jenkins('http://192.168.31.143:8080/', useCrumb=True, username='fengqiyuan', password='fengqiyuan')
    # JWT配置
    JWT_SECRET_KEY = 'testtest'
    # JWT_TOKEN_LOCATION = ['headers', 'cookies', 'json', 'query_string'] # 默认headers
    JWT_TOKEN_SECURE = False
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)


config = {
    'development': DevelopmentConfig,
    'test': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}