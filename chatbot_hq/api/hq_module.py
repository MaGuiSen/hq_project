# -*- coding: utf-8 -*-
import json
import logging
import traceback

from flask import request, Response, Blueprint

from srv.hq_srv import *

_logger = logging.getLogger(__name__)

# flask模块对象
webhook_drug = Blueprint('webhook_drug', __name__)


def construct_response(status, data, code=None, msg=None):
    """
    构建标准请求返回结果
    :param status: 1 为成功
    :param data: 数据内容
    :param code: 错误编码
    :param msg: 错误信息
    :return:
    """
    return json.dumps({u'status': status, u'code': code, u'msg': msg, u'data': data})


def base_func(operate_func):
    results = ''
    try:
        # 获取参数
        action_params_kv = {}
        for p in request.args:
            action_params_kv[p] = request.args[p]
            print p, '=', request.args[p]
        results = operate_func(action_params_kv)
        status = 200
    except Exception as e:
        print str(e)
        _logger.error(traceback.format_exc())
        status = 500
    res_text = construct_response(status, results)
    _logger.debug(res_text)
    return Response(res_text, mimetype='applications/json')

# http://localhost:10011/entity/etl?entity_id=111&biz_key=222
@webhook_drug.route('/entity/etl', methods=['GET'])
def entity_etl():
    def operate(params_req):
        return srv_entity_etl(params_req[u'entity_id'], params_req[u'biz_key'])

    return base_func(operate)