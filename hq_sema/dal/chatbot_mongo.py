#!/usr/bin/env python
# -*- coding: utf-8 -*-

from mongoengine import *
from configparser import ConfigParser


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
__mongo_config = read_config('../config/hq_conf_%s.ini' % (cur_env,))['db.mongo.chatbot']
connect(__mongo_config['db'],
            host=__mongo_config['host'],
            port=int(__mongo_config['port']),
            username=__mongo_config['user'],
            password=__mongo_config['password'])


class Entity(Document):
    """
    实体
    """
    _id = StringField(primary_key=True)
    name = StringField()
    domain_id = StringField(required=True)
    type = StringField(required=True)
    is_active = BooleanField(default=True)
    parent_entities = ListField(StringField())
    semantics = ListField(StringField())
    create_time = DateTimeField()
    create_by = IntField(required=True)
    label_color = StringField()
    meta = {'collection': 'entity', 'strict': False}


class Semantic(Document):
    """
    语义单元
    """
    _id = StringField(primary_key=True)
    domain_id = StringField(required=True)
    name = StringField()
    type = StringField()
    is_active = BooleanField()
    create_time = DateTimeField(required=True)
    create_by = IntField(required=True)
    detail = DictField()

    meta = {'collection': 'semantic', 'strict': False}


class LinkInstance(Document):
    """
    实体-语义列表-链接实例
    """
    _id = StringField(primary_key=True)
    entity_id = StringField()
    semantic_id = StringField()
    biz_entity_id = StringField()
    biz_instance_id = StringField()
    create_time = DateTimeField(required=True)
    create_by = IntField(required=True)

    meta = {'collection': 'link_instance', 'strict': False}


if __name__ == '__main__':
    pass
