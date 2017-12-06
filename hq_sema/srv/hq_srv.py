# -*- coding: utf-8 -*-

from etl.sema_etl import sema_delete, sema_etl_execute


def srv_sema_etl(biz_entity_id, biz_id):
    return sema_etl_execute(biz_entity_id, biz_id)


def srv_sema_del(biz_entity_id, biz_id):
    return sema_delete(biz_entity_id, biz_id)


if __name__ == '__main__':
    pass
