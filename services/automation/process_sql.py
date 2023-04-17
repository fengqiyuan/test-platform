#!/usr/bin/env python
# -*- coding:utf-8 -*-
# time  : 2023/3/31 19:57
# author: fengqiyuan
import re
import sqlparse
from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import Session

from common.logger import logger


def execute_query(check_db, engine):
    sql_script = check_db.get('sql_script', '')
    params = check_db.get('params', {})
    try:
        if not sql_script:
            return "sql不存在"
        sql_script = sql_script.replace("'", '"')
        sql_script = re.sub(r';|--.*', '', sql_script)
        sql_statements = sqlparse.split(sql_script)
        results = []
        with Session(engine) as session:
            for sql in sql_statements:
                parsed = sqlparse.parse(sql.strip())
                first_token = parsed[0].token_first()
                if first_token.normalized not in ('SELECT', 'UPDATE', 'INSERT'):
                    raise ValueError('SQL statement must be a SELECT, UPDATE, or INSERT')
                # 执行SQL
                if params:
                    result = session.execute(text(sql), params)
                else:
                    result = session.execute(text(sql))
                data = [row._asdict() for row in result if result]
                if len(data) == 0:
                    if first_token.normalized == 'SELECT':
                        results.append({})
                elif len(data) == 1:
                    results.append(data[0])
                else:
                    results.append(data)
        if len(results) == 0:
            return {}
        elif len(results) == 1:
            return results[0]
        else:
            return results
    except Exception as e:
        logger.error(e)
