#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2022/10/27 17:07
# author: fengqiyuan
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS


db = SQLAlchemy()
mail = Mail()
cache = Cache()
env_cache = Cache()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()



