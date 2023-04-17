#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/18 09:28
# author: fengqiyuan
import logging
import os
import sys
import time
import datetime


# 找到项目目录
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# 没有log目录则创建目录
log_path = os.path.join(PROJECT_ROOT, "log")
if not os.path.exists(log_path):
    os.mkdir(log_path)

log_file = os.path.join(log_path, "{}_test_platform.log".format(time.strftime("%Y-%m-%d")))

logger = logging.getLogger("test_platform")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s][%(filename)s][line:%(lineno)d][%(levelname)s]%(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S.%f')

file_handler = logging.FileHandler(log_file, mode='a', encoding="UTF-8")
# file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=10)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.DEBUG)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


if __name__ == '__main__':
    logger.info("testmgmt")
    logger.error("error")
    logger.debug("debug")
    logger.warning("warning")
    logger.critical("critical")
