# -*- coding: utf-8 -*-
import logging
from datetime import datetime

from dal.chatbot_mongo import Entity, Semantic
from dal.hq_db import *

# 日志记录对象
from utils.sequtils import gen_unicode_id

_logger = logging.getLogger(__name__)
pw_loggger = logging.getLogger('peewee')
pw_loggger.setLevel(logging.DEBUG)
pw_loggger.addHandler(logging.StreamHandler())

# key为数据库实体的entity_id
# sema_entity_id 为语义实体id
# domain_id领域id
# sema_name_pattern语义词语前缀
# table mysql数据库操作类
base_params = {
    u'obj.common.prod': {
        u'sema_entity_id': u'entity.org.co.company',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'co.company.%s',
        u'table': CoCompany,
    },
    u'obj.idx.co.finan.def': {
        u'sema_entity_id': u'entity.org.co.company',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'co.company.%s',
        u'table': CoCompany,
    },
    u'obj.idx.co.op.def': {
         u'sema_entity_id': u'entity.org.co.company',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'co.company.%s',
        u'table': CoCompany,
    },
    u'obj.org.co.company': {
        u'sema_entity_id': u'entity.org.co.company',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'co.company.%s',
        u'table': CoCompany,
    },
    u'obj.peo.people': {
        u'sema_entity_id': u'entity.org.co.company',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'co.company.%s',
        u'table': CoCompany,
    },
}


# TODO..错误的返回
def sema_etl_execute(biz_entity_id, biz_id):
    entity = base_params.get(biz_entity_id)

    if not entity:
        print u'根据biz_entity_id找不到实体类型'
        return

    sema_entity_id = entity.get(u'sema_entity_id', u'')
    domain_id = entity.get(u'domain_id', u'')
    sema_name_pattern = entity.get(u'sema_name_pattern', u'')
    table = entity.get(u'table', u'')

    if not domain_id:
        print u'未找到domain_id'
        return

    if not table:
        print u'未找到table'
        return

    if not sema_entity_id:
        print u'未找到sema_entity_id'
        return

    # biz_entity_id、biz_id: mysql数据库的entity_id、id
    mq_result = table.select().where(table.entity_id == biz_entity_id, table.id == biz_id)
    if not mq_result:
        return

    mq_result = mq_result[0]

    # 判断是否需要更新，从时间上判断
    mq_create_at = mq_result.create_at
    mq_update_at = mq_result.update_at
    sema_etl_at = mq_result.sema_etl_at

    if sema_etl_at and (sema_etl_at >= mq_create_at and sema_etl_at >= mq_update_at):
        # 不需要更新
        return

    phrase_list = []

    mq_id = mq_result.id
    name = mq_result.default_name

    # TODO...给数据库添加对应字段
    name_list = [
        name,
        mq_result.name_cn,
        mq_result.name_cn_s,
        mq_result.name_en,
        mq_result.name_en_s
    ]

    # 从alias库获取别名
    alias_result = EavInsAlias.select().where(EavInsAlias.entity_id == biz_entity_id,
                                              EavInsAlias.instance_id == mq_id,
                                              EavInsAlias.alias.is_null(False))
    if alias_result:
        alias = alias_result[0].alias.split(u',')
        name_list += alias

    for name_value in name_list:
        if name_value and name_value not in phrase_list:
            phrase_list.append(name_value)

    detail = {
        u"phrase_list": phrase_list,
        u"biz_entity_id": biz_entity_id,
        u"biz_id": biz_id,
        u"name": name,
    }

    semantic = Semantic.objects(
        __raw__={u"$and": [{u"detail.biz_entity_id": biz_entity_id}, {u"detail.biz_id": biz_id}]})

    if semantic:
        semantic = semantic[0]
        # 存在了，就更新
        semantic.detail = detail
        semantic.create_by = 0
    else:
        # 不存在，则新增
        sema_id = gen_unicode_id()
        semantic = Semantic(_id=sema_id,
                            domain_id=domain_id,
                            name=sema_name_pattern % name,  # 语义名称
                            type=u'list',
                            is_active=True,
                            create_time=datetime.now(),
                            create_by=0,
                            detail=detail
                            )
        # 更新实体 TODO..如果失败了，可能导致下一次，没办法关联
        entity = Entity.objects(_id=sema_entity_id)
        if entity:
            entity = entity[0]
            entity.semantics.append(sema_id)
            entity.save()
    semantic.save()

    # 更新sema_etl时间
    table.update(sema_etl_at=datetime.now()).where(table.id == biz_id).execute()


if __name__ == '__main__':
    print u'导入语义数据'
    sema_etl_execute(u'obj.org.co.company', u'00005.obj.org.co.company.')
