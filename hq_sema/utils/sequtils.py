# -*- coding: utf-8 -*-

import uuid
from datetime import datetime
import string
import random


def getUuid1():
    """
    获取根据mac地址生成的全球唯一id
    :return: 字符串
    """
    return str(uuid.uuid1())


def base_str():
    return (string.letters + string.digits)


def key_gen(leng):
    keylist = [random.choice(base_str()) for i in range(leng)]
    return ("".join(keylist))


def gen_mongo_id():
    return datetime.now().strftime('%y%m%d%H%M%S') + unicode(datetime.now().microsecond / 1000) + key_gen(5)

def gen_unicode_id(length=25):
    result =  datetime.now().strftime('%y%m%d%H%M%S') + unicode(datetime.now().microsecond / 1000)
    if len(result) < length:
        remain = length - len(result)
        result += key_gen(remain)
    return result

if __name__ == '__main__':
    id = gen_unicode_id()
    print id
