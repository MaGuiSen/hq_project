# -*- coding: utf-8 -*-

from qbot.qbotsdk import *
import requests
import traceback


class WebhookExecutor(object):
    """
    web hook 执行器
    """
    @staticmethod
    def post(app_id, url, params):
        try:
            signature = u''
            timestamp = int(time.time())
            if url is None or len(url)<=0:
                raise Exception(u'url is empty!')
            url += u'?app_id=%s&signature=%s&timestamp=%d' %(app_id, signature, timestamp)
            print u'调用webhook请求:' + url

            # body
            body_value = json.dumps(params)

            # 执行请求
            response = requests.post(url, data=body_value)

            if response.status_code != 200:
                raise Exception(u'请求url: %s, 返回结果状态异常：%s' %(url, response.status_code))

            return response.content
        except:
            print traceback.format_exc()
            return None
