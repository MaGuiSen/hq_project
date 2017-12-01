# -*- coding: utf-8 -*-

import time
import uuid
import json
import string, random
from datetime import datetime

class ChannelAccount(dict):
    """
    渠道
    """
    def __init__(self, id=None, name=None):
        super(ChannelAccount, self).__init__()
        self[u'id'] = id
        self[u'name'] = name

    def get_id(self):
        return self.get(u'id', None)

    def set_id(self, value):
        self[u'id'] = value

    def get_name(self):
        return self.get(u'name', None)

    def set_name(self, value):
        self[u'name'] = value


class ConversationAccount(dict):
    """
    会话，一个会话可以是用户和BOT，也可能是多人的
    """
    def __init__(self, id=None, name=None, is_group=False):
        super(ConversationAccount, self).__init__()
        self[u'id'] = id
        self[u'name'] = name
        self[u'is_group'] = is_group  # 是否是群聊会话

    def get_id(self):
        return self.get(u'id', None)

    def set_id(self, value):
        self[u'id'] = value

    def get_name(self):
        return self.get(u'name', None)

    def set_name(self, value):
        self[u'name'] = value

    def get_is_group(self):
        return self.get(u'is_group', None)

    def set_is_group(self, value):
        self[u'is_group'] = value


class ActivityTypes(object):
    """
    bot消息协议类型
    """

    message = u'message'  # 普通消息
    event = u'event'  # 事件
    conversationUpdate = u'conversationUpdate'  # 会话更新


class Activity(dict):
    """
    bot一次沟通的消息协议
    """
    def __init__(self):
        super(Activity, self).__init__()
        self[u'type'] = ActivityTypes.message
        self[u'id'] = self.__gen_id()
        self[u'timestamp'] = int(time.time()*1000)  # 时间戳,整型
        self[u'localTimestamp'] = int(time.time()*1000)  # 本地时间
        self[u'serviceUrl'] = None  # connnect服务的url
        self[u'channelId'] = None  # 渠道id
        self[u'from'] = None  # 来源 ChannelAccount
        self[u'conversation'] = None  # 会话 ConversationAccount
        self[u'recipient'] = None  # 接收方 ChannelAccount
        self[u'textFormat'] = None  # 文本格式
        self[u'attachmentLayout'] = None
        self[u'membersAdded'] = []  # ChannelAccount 列表
        self[u'membersRemoved'] = []  # ChannelAccount 列表
        self[u'historyDisclosed'] = False
        self[u'locale'] = None  # 区域设置
        self[u'lang'] = u'en'  # 语言设置
        self[u'text'] = None  # text
        self[u'speak'] = None
        self[u'inputHint'] = None
        self[u'summary'] = None  # summary
        self[u'suggestedActions'] = {}
        self[u'channelData'] = {}
        self[u'attachments'] = []  # 附加消息列表
        self[u'entities'] = []  # 附加实体列表
        self[u'name'] = None  # name
        self[u'replyToId'] = None  # 针对哪个来源消息的id回复

    def get_attachments(self):
        return self[u'attachments']

    def add_attachment(self, attachment):
        """
        添加附件，附件可以是Attachment或各类Card
        :param attachment:
        :return:
        """
        self[u'attachments'].append(attachment)

    def create_reply(self):
        """
        构建回复消息
        :return: Activity | None
        """
        activity = Activity()
        activity[u'type'] = ActivityTypes.message
        activity[u'id'] = self.__gen_id()
        activity[u'timestamp'] = int(time.time()*1000)  # 时间戳,整型
        activity[u'localTimestamp'] = int(time.time()*1000)  # 本地时间
        activity[u'serviceUrl'] = self[u'serviceUrl']  # connnect服务的url
        activity[u'channelId'] = self[u'channelId']  # 渠道id
        activity[u'from'] = self[u'recipient']  # 来源 ChannelAccount
        activity[u'conversation'] = self[u'conversation']  # 会话 ConversationAccount
        activity[u'recipient'] = self[u'from']  # 接收方 ChannelAccount
        activity[u'textFormat'] = u"plain"  # 文本格式
        activity[u'attachment_layout'] = None
        activity[u'membersAdded'] = []  # ChannelAccount 列表
        activity[u'membersRemoved'] = []  # ChannelAccount 列表
        activity[u'locale'] = self[u'locale']  # 区域设置
        activity[u'lang'] = self[u'lang']  # 语言设置
        activity[u'text'] = None  # text
        activity[u'summary'] = None  # summary
        activity[u'attachments'] = []  # 附加消息列表
        activity[u'entities'] = []  # 附加实体列表
        activity[u'name'] = None  # name
        activity[u'replyToId'] = self[u'id']  # 针对哪个来源消息的id回复
        return activity

    def from_json(self, json_unicode):
        """
        从json中构建
        :param json_unicode:
        :return:
        """
        dict_obj = json.loads(json_unicode)
        for key in dict_obj:
            if key == u'text':
                # 处理输入非字符串的情况
                if not isinstance(dict_obj.get(u'text', None), unicode):
                    self[u'text'] = unicode(dict_obj.get(u'text', ''))
                else:
                    self[u'text'] = dict_obj.get(u'text', u'')
            elif key == u'from':
                from_account = ChannelAccount(id=dict_obj[key].get(u'id', None), name=dict_obj[key].get(u'name', None))
                self[u'from'] = from_account
            elif key == u'recipient':
                recipient_account = ChannelAccount(id=dict_obj[key].get(u'id', None), name=dict_obj[key].get(u'name', None))
                self[u'recipient'] = recipient_account
            elif key == u'conversation':
                conv = ConversationAccount(id=dict_obj[key].get(u'id', None), name=dict_obj[key].get(u'name', None), is_group=dict_obj[key].get(u'isGroup', False))
                self[u'conversation'] = conv
            else:
                self[key] = dict_obj[key]

    def get_type(self):
        """
        获取type
        :return: unicode | None
        """
        return self.get(u'type', None)

    def set_type(self, value):
        """
        设置type
        :param value:
        :return:
        """
        self[u'type'] = value

    def get_id(self):
        return self.get(u'id', None)

    def set_id(self, value):
        self[u'id'] = value

    def get_text(self):
        """
        获取text
        :return: unicode | None
        """
        return self.get(u'text', None)

    def set_text(self, value):
        """
        设置text
        :param value:
        :return:
        """
        self[u'text'] = value

    def get_lang(self):
        return self.get(u'lang', None)

    def set_lang(self, value):
        self[u'lang'] = value

    def get_locale(self):
        return self.get(u'locale', None)

    def set_locale(self, value):
        self[u'locale'] = value

    def get_service_url(self):
        """
        获取service_url
        :return: unicode | None
        """
        return self.get(u'serviceUrl', None)

    def set_service_url(self, value):
        """
        设置service_url
        :param value:
        :return:
        """
        self[u'serviceUrl'] = value

    def get_channel_id(self):
        """
        获取channel_id
        :return: unicode | None
        """
        return self.get(u'channelId', None)

    def set_channel_id(self, value):
        """
        设置channel_id
        :param value:
        :return:
        """
        self[u'channelId'] = value

    def get_from(self):
        """
        获取from
        :return: ChannelAccount | None
        """
        return self.get(u'from', None)

    def set_from(self, value):
        """
        设置from
        :param value:
        :return:
        """
        self[u'from'] = value

    def get_recipient(self):
        """
        获取recipient
        :return: ChannelAccount | None
        """
        return self.get(u'recipient', None)

    def set_recipient(self, value):
        """
        设置recipient
        :param value:
        :return:
        """
        self[u'recipient'] = value

    def get_conversation(self):
        """
        获取conversation
        :return: ConversationAccount | None
        """
        return self.get(u'conversation', None)

    def set_conversation(self, value):
        """
        设置conversation
        :param value:
        :return:
        """
        self[u'conversation'] = value

    def __base_str(self):
        return (string.letters + string.digits)

    def __key_gen(self):
        keylist = [random.choice(self.__base_str()) for i in range(5)]
        return ("".join(keylist))

    def __gen_id(self):
        return datetime.now().strftime('%y%m%d%H%M%S') + unicode(datetime.now().microsecond / 1000) + self.__key_gen()


class Fulfillment(dict):
    """
    Action 结果
    """
    def __init__(self):
        super(Fulfillment, self).__init__()
        self[u'status'] = 200  # 状态200是正常，500服务异常
        self[u'code'] = u''  # 状态异常编号
        self[u'message'] = u''  # 状态异常消息
        self[u'activities'] = []

    def get_status(self):
        return self[u'status']

    def set_status(self, value):
        self[u'status'] = value

    def get_code(self):
        return self[u'code']

    def set_code(self, value):
        self[u'code'] = value

    def get_message(self):
        """
        此处的message是状态消息
        :return:
        """
        return self[u'message']

    def set_message(self, value):
        self[u'message'] = value

    def get_activities(self):
        return self[u'activities']

    def has_activity(self):
        """
        判断是否有返回结果
        :return:
        """
        if len(self[u'activities']) <= 0:
            return False
        else:
            return True

    def add_activity(self, activity):
        self[u'activities'].append(activity)


class ContentType(object):
    """
    内容类型
    """
    text = u'application/vnd.microsoft.text'
    hero_card = u'application/vnd.microsoft.card.hero'
    thumbnail_card = u'application/vnd.microsoft.card.thumbnail'
    receipt_card = u'application/vnd.microsoft.card.receipt'
    signin_card = u'application/vnd.microsoft.card.signin'
    image_attachment = u'image/png'
    adaptive_card = u'adaptivecard'


class ButtonActionEnum(object):
    """
    Button Actions 事件类型
    """
    open_url = u'openUrl'
    im_back = u'imBack'
    post_back = u'postBack'
    call = u'call'
    play_audio = u'playAudio'
    play_video = u'playVideo'
    show_image = u'showImage'
    download_file = u'downloadFile'
    signin = u'signin'


class Attachment(dict):
    """
    附件
    """
    def __init__(self, content_url=None, content_type=None, name=None):
        super(Attachment, self).__init__()
        self[u'content_url'] = content_url
        self[u'content_type'] = content_type
        self[u'name'] = name


class CardAction(dict):
    """
    按钮模型
    """
    def __init__(self, type=None, title=None, value=None, image=None):
        super(CardAction, self).__init__()
        self[u'type'] = type
        self[u'title'] = title
        self[u'value'] = value
        self[u'image'] = image

    def get_type(self):
        return self.get(u'type', None)

    def set_type(self, value):
        self[u'type'] = value

    def get_title(self):
        return self.get(u'title', None)

    def set_title(self, value):
        self[u'title'] = value

    def get_value(self):
        return self.get(u'value', None)

    def set_value(self, value):
        self[u'value'] = value

    def get_image(self):
        return self.get(u'image', None)

    def set_image(self, value):
        self[u'image'] = value


class CardImage(dict):
    """
    图片模型
    """
    def __init__(self, url=None, alt=None, card_action=None):
        super(CardImage, self).__init__()
        self[u'url'] = url
        self[u'alt'] = alt
        self[u'tap'] = card_action

    def get_url(self):
        return self.get(u'url', None)

    def set_url(self, value):
        self[u'url'] = value

    def get_alt(self):
        return self.get(u'alt', None)

    def set_alt(self, value):
        self[u'alt'] = value

    def get_tap(self):
        """
        tap是触摸事件，CardAction
        :return:
        """
        return self.get(u'tap', None)

    def set_tap(self, value):
        """
        tap是触摸事件，CardAction
        :param value:
        :return:
        """
        self[u'tap'] = value


class HeroCard(dict):
    """
    Hero卡片模型
    """
    def __init__(self, title=None, subtitle=None, text=None, images=None, buttons=None, tap=None):
        super(HeroCard, self).__init__()
        self[u'contentType'] = ContentType.hero_card
        self[u'content'] = {}
        self[u'content'][u'title'] = title
        self[u'content'][u'subtitle'] = subtitle
        self[u'content'][u'text'] = text
        self[u'content'][u'images'] = [] if images is None else images
        self[u'content'][u'buttons'] = [] if buttons is None else buttons
        self[u'content'][u'tap'] = tap

    def get_title(self):
        return self[u'content'].get(u'title', None)

    def set_title(self, value):
        self[u'content'][u'title'] = value

    def get_subtitle(self):
        return self[u'content'].get(u'subtitle', None)

    def set_subtitle(self, value):
        self[u'content'][u'subtitle'] = value

    def get_text(self):
        return self[u'content'].get(u'text', None)

    def set_text(self, value):
        self[u'content'][u'text'] = value

    def get_images(self):
        return self[u'content'].get(u'images', [])

    def set_images(self, value):
        self[u'content'][u'images'] = value

    def get_buttons(self):
        return self[u'content'].get(u'buttons', [])

    def set_buttons(self, value):
        self[u'content'][u'buttons'] = value

    def get_tap(self):
        return self[u'content'].get(u'tap', None)

    def set_tap(self, value):
        self[u'content'][u'tap'] = value


class Parameter(dict):
    """
    参数运行时
    definition: 参数的定义时信息，不同系统使用botflow时，会有区别
    """

    def __init__(self, required=True, data_type=None, name=None, value=None, is_list=False, definition=None):
        super(Parameter, self).__init__()
        self[u'required'] = required
        self[u'dataType'] = data_type
        self[u'name'] = name
        self[u'value'] = value
        self[u'isList'] = is_list
        self[u'attempts'] = 0  # 实际的错误尝试次数(配置的默认最大尝试次数为3，如果配置为0，一旦错误直接结束流程，转到新的intent命中过程)
        self[u'definition'] = definition

    def get_attempts(self):
        return self[u'attempts']

    def add_attempt_count(self):
        self[u'attempts'] += 1

    def is_required(self):
        return self.get(u'required', False)

    def set_is_required(self, value):
        self[u'required'] = value

    def get_data_type(self):
        return self.get(u'dataType', None)

    def set_data_type(self, value):
        self[u'dataType'] = value

    def get_name(self):
        return self.get(u'name', None)

    def set_name(self, value):
        self[u'name'] = value

    def get_value(self):
        return self.get(u'value', None)

    def set_value(self, value):
        self[u'value'] = value

    def is_list(self):
        return self.get(u'is_list', False)

    def set_is_list(self, value):
        self[u'is_list'] = value

    def get_definition(self):
        return self.get(u'definition', None)

    def set_definition(self, value):
        self[u'definition'] = value
