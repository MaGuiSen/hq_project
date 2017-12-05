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
        u'sema_entity_id': u'entity.common.co.product',
        u'domain_id': u'domain.common.co.product',
        u'sema_name_pattern': u'product.%s',
        u'table': CoMajorProd,
    },
    u'obj.idx.co.finan.def': {
        u'sema_entity_id': u'entity.idx.co.finan.defi',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'idx.finan.%s',
        u'table': CoIdxDefFinan,
    },
    u'obj.idx.co.op.def': {
        u'sema_entity_id': u'entity.idx.co.op.def',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'idx.op.%s',
        u'table': CoIdxDefOp,
    },
    u'obj.org.co.company': {
        u'sema_entity_id': u'entity.org.co.company',
        u'domain_id': u'domain.org.co.company',
        u'sema_name_pattern': u'co_company.%s',
        u'table': CoCompany,
    },
    u'obj.peo.people': {
        u'sema_entity_id': u'entity.peo.co.executives',
        u'domain_id': u'domain.peo.co.executives',
        u'sema_name_pattern': u'co_executives.%s',
        u'table': PeoPeople,
    },
}


def sema_delete(biz_entity_id, biz_id):
    # 找到语义删除，同时删除关联
    entity_config = base_params.get(biz_entity_id)
    sema_entity_id = entity_config.get(u'sema_entity_id', u'')

    semantic = Semantic.objects(
        __raw__={u"$and": [{u"detail.biz_entity_id": biz_entity_id}, {u"detail.biz_id": biz_id}]})
    if semantic:
        semantic = semantic[0]
        sema_id = semantic._id
        # 删除操作
        semantic.delete()
        save_log(u'删除语义')
        # 找下关联关系
        entity = Entity.objects(_id=sema_entity_id, semantics=sema_id)
        if entity:
            save_log(u'删除实体语义关联')
            entity = entity[0]
            entity.semantics.remove(sema_id)
            entity.save()
        # TODO..测试看是否需要更新etl时间
        return back_info(200, u'删除成功')
    else:
        return back_info(500, u'未找到相关语义数据')


# 定时补
def sema_etl_timing_execute():
    for biz_entity_id in base_params:
        entity_config = base_params.get(biz_entity_id)

        sema_entity_id = entity_config.get(u'sema_entity_id', u'')
        domain_id = entity_config.get(u'domain_id', u'')
        sema_name_pattern = entity_config.get(u'sema_name_pattern', u'')
        table = entity_config.get(u'table', u'')

        sql_str = (u'entity_id="%s" and (sema_etl_at is null or sema_etl_at<create_at or sema_etl_at<update_at) '
                   u'and (is_delete="0" or is_delete is null)') % biz_entity_id
        pw_loggger.info(sql_str)

        # 分页操作
        def page_operate():
            mq_result_all = table.select().where(SQL(sql_str)).paginate(1, 1000)
            if not mq_result_all:
                # 结束循环
                return True
            save_log(u'长度%s ' % (len(mq_result_all)))
            # 分页查询
            for mq_result in mq_result_all:
                biz_id = mq_result.id
                base_execute(table, mq_result, biz_entity_id, biz_id, domain_id, sema_name_pattern, sema_entity_id)

        def page_run(operate):
            page_index = 1
            while True:
                save_log(u'%s 处理第%s页' % (biz_entity_id, page_index))
                if operate():
                    save_log(u'%s 结束循环，最后一页：%s' % (biz_entity_id, page_index))
                    break
                page_index += 1
                save_log(u'\n')
        save_log(u'\n')
        save_log(u'开始%s的循环遍历' % biz_entity_id)
        page_run(page_operate)


def back_info(code, msg):
    save_log(u'code %s， msg：%s' % (code, msg))
    return code, msg


def save_log(log):
    pw_loggger.info(log)
    log = log.encode('utf8')
    with open('operate.txt', 'a') as loadF:
        loadF.write(log)
        loadF.close()


def sema_etl_execute(biz_entity_id, biz_id):
    entity_config = base_params.get(biz_entity_id)

    if not entity_config:
        return back_info(500, u'根据biz_entity_id找不到实体类型配置')

    sema_entity_id = entity_config.get(u'sema_entity_id', u'')
    domain_id = entity_config.get(u'domain_id', u'')
    sema_name_pattern = entity_config.get(u'sema_name_pattern', u'')
    table = entity_config.get(u'table', u'')

    if not domain_id:
        return back_info(500, u'未找到domain_id')

    if not table:
        return back_info(500, u'未找到table')

    if not sema_entity_id:
        return back_info(500, u'未找到sema_entity_id')

    # biz_entity_id、biz_id: mysql数据库的entity_id、id
    sql_str = u'entity_id="%s" and id="%s" and (is_delete="0" or is_delete is null)' % (biz_entity_id, biz_id)
    mq_result = table.select().where(SQL(sql_str))
    if not mq_result:
        return back_info(500, u'未找到相关数据')

    mq_result = mq_result[0]

    # 判断是否需要更新，从时间上判断
    mq_create_at = mq_result.create_at
    mq_update_at = mq_result.update_at
    sema_etl_at = mq_result.sema_etl_at

    if sema_etl_at and (sema_etl_at >= mq_create_at and sema_etl_at >= mq_update_at):
        return back_info(200, u'已经更新到最新')

    base_execute(table, mq_result, biz_entity_id, biz_id, domain_id, sema_name_pattern, sema_entity_id)

    return back_info(200, u'已经更新到最新')


def base_execute(table, mq_result, biz_entity_id, biz_id, domain_id, sema_name_pattern, sema_entity_id):
    phrase_list = []

    mq_id = mq_result.id

    name = mq_result.default_name if hasattr(mq_result, 'default_name') else ''
    name_cn = mq_result.name_cn if hasattr(mq_result, 'name_cn') else ''
    name_cn_s = mq_result.name_cn_s if hasattr(mq_result, 'name_cn_s') else ''
    name_en = mq_result.name_en if hasattr(mq_result, 'name_en') else ''
    name_en_s = mq_result.name_en_s if hasattr(mq_result, 'name_en_s') else ''

    name_list = [
        name,
        name_cn,
        name_cn_s,
        name_en,
        name_en_s
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

    save_log(u'处理entity_id：%s， biz_id：%s，name： %s ' % (biz_entity_id, biz_id, name))
    save_log(u'得到phrase_list：%s' % u','.join(phrase_list))
    detail = {
        u"phrase_list": phrase_list,
        u"biz_entity_id": biz_entity_id,
        u"biz_id": biz_id,
    }

    semantic = Semantic.objects(
        __raw__={u"$and": [{u"detail.biz_entity_id": biz_entity_id}, {u"detail.biz_id": biz_id}]})

    if semantic:
        semantic = semantic[0]
        sema_id = semantic._id
        save_log(u'存在并更新语义，语义id为sema_id：%s' % sema_id)
        # 存在了，就更新
        semantic.detail = detail
        semantic.create_by = 0
        semantic.name = sema_name_pattern % name
    else:
        # 不存在，则新增
        sema_id = gen_unicode_id()
        save_log(u'不存在并新增语义，语义id为sema_id：%s' % sema_id)
        semantic = Semantic(_id=sema_id,
                            domain_id=domain_id,
                            name=sema_name_pattern % name,  # 语义名称
                            type=u'list',
                            is_active=True,
                            create_time=datetime.now(),
                            create_by=0,
                            detail=detail
                            )
    semantic.save()

    # 实体更新，先判断关联是否存在，不存在则需要添加，目的是防止一次更新失败之后不能正常更新关联关系
    entity = Entity.objects(_id=sema_entity_id, semantics=sema_id)
    if not entity:
        entity = Entity.objects(_id=sema_entity_id)
        if entity:
            save_log(u'新增实体语义关联')
            entity = entity[0]
            entity.semantics.append(sema_id)
            entity.save()

    # 更新sema_etl时间
    table.update(sema_etl_at=datetime.now()).where(table.id == biz_id).execute()
    save_log(u'etl完成')
    save_log(u'\n')


# 171205142303365tItYVf8SuX
if __name__ == '__main__':
    # code, msg = sema_etl_execute(u'obj.org.co.company', u'000001.obj.org.co.company.')
    sema_etl_timing_execute()
    # sema_delete(u'obj.org.co.company', u'000001.obj.org.co.company.')