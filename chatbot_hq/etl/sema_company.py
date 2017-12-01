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

DOMAIN_ID = u'domain.org.co.company'  # 领域ID
sema_entity_id = u'entity.org.co.company'  # 语义实体id(注意长度不能是24，PHP有异常，切记）


class BaseIngestion(object):
    @staticmethod
    def is_need_etl():
        pass


class CoCompanySemaIngestion(BaseIngestion):
    @staticmethod
    def import_instance(biz_entity_id, biz_id):
        domain_id = DOMAIN_ID
        sema_name_pattern = u'co.company.%s'  # 语义名称 TODO..封装成方法

        # biz_entity_id、biz_id: mysql数据库的entity_id、id
        mq_result = CoCompany.select().where(CoCompany.entity_id == biz_entity_id, CoCompany.id == biz_id)
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
        CoCompany.update(sema_etl_at=datetime.now()).where(CoCompany.id == biz_id).execute()


if __name__ == '__main__':
    print u'导入语义数据'
    # CoCompanySemaIngestion.import_instance(u'obj.org.co.company', u'00004.obj.org.co.company.')
    a = {}
    print a.get("dd")