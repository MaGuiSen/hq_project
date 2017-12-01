# -*- coding: utf-8 -*-

"""
用于测试drug_module请求
"""

from qbot.console_client import *

APP_ID_HYS = u'73677F51-F2DC-3D06-AA6C-094F917BDBAD'
URL_BASE = u'http://0.0.0.0:10011'
CHAN_ID = u'console_client'
CONV_ID = u'console_client'
FROM_ID = u'console_client'


def get_default_post_data(q=u''):

    # 获取参数
    app_id = APP_ID_HYS
    chan_id = CHAN_ID
    conv_id = CONV_ID
    from_id = FROM_ID

    # 构建activity
    activity = Activity()
    activity.set_channel_id(chan_id)
    activity.set_conversation(ConversationAccount(id=conv_id, name=conv_id, is_group=False))
    activity.set_from(ChannelAccount(id=from_id, name=from_id))
    activity.set_recipient(ChannelAccount(id=chan_id, name=chan_id))
    activity.set_text(q)

    action_params = []
    action_param = Parameter(required=True,
                          data_type=u'string',
                          name=u'iid',
                          is_list=False,
                          value=u'client_console',
                          definition=None)
    action_params.append(action_param)

    data = {
        u'action_params': action_params,
        u'q': activity,
        u'lang': u'zh-cn'
    }

    return data


def test_drug_hello(q=u'hello'):

    url = URL_BASE + u'/drug/hello'
    body = get_default_post_data(q)

    # 添加一个参数
    action_param = Parameter(required=True,
                          data_type=u'string',
                          name=u'my_name',
                          is_list=False,
                          value=u'郭星晖',
                          definition=None)
    body[u'action_params'].append(action_param)

    print WebhookExecutor.post(app_id=APP_ID_HYS, url=url, params=body)


if __name__ == '__main__':
    test_drug_hello()