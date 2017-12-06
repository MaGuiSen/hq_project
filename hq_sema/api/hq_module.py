# -*- coding: utf-8 -*-
import json
import logging
import traceback

from flask import request, Response, Blueprint

from srv.hq_srv import *

_logger = logging.getLogger(__name__)

# flask模块对象
hq_sema_etl = Blueprint('hq_sema_etl', __name__)


def construct_response(code, msg=None, data=None):
    """
    构建标准请求返回结果
    :param data: 数据内容
    :param code: 错误编码
    :param msg: 错误信息
    """
    return json.dumps({u'code': code, u'msg': msg, u'data': data})


def base_func(operate_func):
    try:
        # 获取参数
        action_params_kv = {}
        for p in request.args:
            action_params_kv[p] = request.args[p]
            print p, '=', request.args[p]
        code, msg = operate_func(action_params_kv)
    except Exception as e:
        _logger.error(traceback.format_exc())
        code = 500
        msg = str(e)
        print msg
    res_text = construct_response(code, msg)
    _logger.debug(res_text)
    return res_text  # Response(res_text, mimetype='applications/json')


# http://localhost:10011/sema/etl?biz_entity_id=111&biz_id=222
@hq_sema_etl.route('/sema/etl', methods=['GET'])
def sema_etl():
    def operate(params_req):
        return srv_sema_etl(params_req[u'biz_entity_id'], params_req[u'biz_id'])

    return base_func(operate)


# http://localhost:10011/sema/delete?biz_entity_id=obj.org.co.company&biz_id=000001.obj.org.co.company.
@hq_sema_etl.route('/sema/delete', methods=['GET'])
def sema_delete():
    def operate(params_req):
        return srv_sema_del(params_req[u'biz_entity_id'], params_req[u'biz_id'])

    return base_func(operate)
