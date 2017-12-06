# -*- coding: utf-8 -*-

"""
用于测试drug_module请求
"""
import json

import requests


def test_etl():
    biz_entity_id = 'obj.org.co.company'
    biz_id = '000001.obj.org.co.company.'
    response = requests.get("http://localhost:10011/sema/etl?biz_entity_id=%s&biz_id=%s" % (biz_entity_id, biz_id), timeout=5)
    response_obj = json.loads(response.text)
    print "code:", response_obj.get("code")
    print "msg:", response_obj.get("msg")


def test_del():
    biz_entity_id = 'obj.org.co.company'
    biz_id = '000001.obj.org.co.company.'
    response = requests.get("http://localhost:10011/sema/delete?biz_entity_id=%s&biz_id=%s" % (biz_entity_id, biz_id), timeout=5)
    response_obj = json.loads(response.text)
    print "code:", response_obj.get("code")
    print "msg:", response_obj.get("msg")


if __name__ == '__main__':
    test_etl()
