#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser
from playhouse.shortcuts import RetryOperationalError
from sqlalchemy import create_engine
from peewee import *


# 数据库配置相关

def read_config(file_name):
    parser = ConfigParser()
    parser.read(file_name)
    result = {}
    for sec in parser.sections():
        items = parser.items(sec)

        item_dict = {}
        for item in items:
            item_dict[item[0]] = item[1]
        result[sec] = item_dict
    return result


cur_env = read_config('../config/env.ini')['env']['active']
hys_spider_db_conf = read_config('../config/hq_conf_%s.ini' % (cur_env,))['db.mysql.qs_hq_beta']


# 数据库连接对象相关

def create_engine_4_mysql(conf=None):
    """
    构建mysql的执行引擎
    :param conf:
    :return:
    """
    engine = create_engine('mysql+mysqlconnector://%s:%s@%s:%s/%s' % (
    str(conf['user']), str(conf['password']), str(conf['host']), str(conf['port']), str(conf['database'])),
                           pool_recycle=3600, echo=False)
    return engine


def hys_spider_engine():
    """
    fund_cn db的访问引擎，pandas或SqlArchemy使用
    :return:
    """
    return create_engine_4_mysql(conf=hys_spider_db_conf)


class RetryMySQLDatabase(RetryOperationalError, MySQLDatabase):
    pass


hys_spider_db = RetryMySQLDatabase(
    hys_spider_db_conf['database'],
    user=str(hys_spider_db_conf['user']),
    password=str(hys_spider_db_conf['password']),
    host=str(hys_spider_db_conf['host']),
    port=int(hys_spider_db_conf['port']),
    threadlocals=False,
)


# 物理模型

class BaseModel(Model):
    class Meta:
        database = hys_spider_db


class CoCompany(BaseModel):
    id = CharField(null=True)
    entity_id = CharField(null=True)
    default_name = CharField(null=True)
    update_at = DateTimeField(null=True)
    create_at = DateTimeField(null=True)
    sema_etl_at = DateTimeField(null=True)
    is_delete = CharField(null=True)

    name_cn = CharField(null=True)
    name_cn_s = CharField(null=True)
    name_en = CharField(null=True)
    name_en_s = CharField(null=True)

    class Meta:
        db_table = 'co_company'


class EavInsAlias(BaseModel):
    id = CharField(null=True)
    entity_id = CharField(null=True)
    instance_id = CharField(null=True)
    alias = CharField(null=True)

    class Meta:
        db_table = 'eav_ins_alias'
