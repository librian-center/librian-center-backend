import logging
import uuid
import hashlib
import types
import json
import time
import random

from azure.cosmosdb.table import TableService, Entity
from azure.common import AzureMissingResourceHttpError
from azure.cosmosdb.table.models import TablePayloadFormat

from . import config
from .utils import 莉沫Error


class rimoTableService(TableService):
    def get_entity(self, *li, **d):
        t = super().get_entity(*li, **d)
        if 'etag' in t:
            del t['etag']
        if 'Timestamp' in t:
            del t['Timestamp']
        return t
    
    def goku_query_entities(self, *li, **d):
        t = list(super().query_entities(*li, **d))
        for i in t:
            if 'etag' in i:
                del i['etag']
            if 'Timestamp' in i:
                del i['Timestamp']
        return t


表服务 = rimoTableService(connection_string=config.STORAGE_CONNECTION_STRING)
用户表 = 'user'
事件表 = 'act'


def _hs(s):
    s += config.SALT
    h = hashlib.md5()
    h.update(s.encode(encoding='utf-8'))
    return h.hexdigest()


def _生成灵牌(RowKey):
    真密码 = 表服务.get_entity(用户表, 'q', RowKey)['密码']
    return {'RowKey': RowKey, '密码哈希': _hs(真密码)}


def _灵牌验证(灵牌):
    真密码 = 表服务.get_entity(用户表, 'q', 灵牌['RowKey'])['密码']
    return _hs(真密码) == 灵牌['密码哈希']


def 问好(名字='9'):
    return f'你好，{名字}！'


def 登录(RowKey, 密码):
    真密码 = 表服务.get_entity(用户表, 'q', RowKey)['密码']
    assert 密码 == 真密码, '密码错误。'
    return _生成灵牌(RowKey)


def 注册(RowKey, 密码, 邮箱):
    assert len(RowKey) < 64, '用户名不能超过63字符。'
    assert len(密码) < 64, '密码不能超过63字符。'
    try:
        查询基本信息(RowKey)
        raise 莉沫Error('别人用了这个用户名了。')
    except AzureMissingResourceHttpError:
        None
    信息 = {
        'PartitionKey': 'q',
        'RowKey': RowKey,
        '名字': RowKey,
        '邮箱': 邮箱,
        '注册时间': time.time(),
        '密码': 密码,
    }
    表服务.insert_entity(用户表, 信息)
    return _生成灵牌(RowKey)


def 修改头像(流, 灵牌):
    from . import 图像处理
    from . import 文件存储
    大头像, 小头像 = 图像处理.做头(流)
    大md5 = 文件存储.上传(大头像, 'avatar')
    小md5 = 文件存储.上传(小头像, 'avatar')
    新信息 = {
        'PartitionKey': 'q',
        'RowKey': 灵牌['RowKey'],
        '大头像': 大md5,
        '小头像': 小md5,
    }
    表服务.merge_entity(用户表, 新信息)


def 查询详细信息(RowKey, 灵牌):
    assert 灵牌['RowKey'] == RowKey, '灵牌权限无效。'
    人 = 表服务.get_entity(用户表, 'q', RowKey,
                       select='RowKey, 名字, 大头像, 小头像, 简介, 邮箱, 公开邮箱, 注册时间'
                       )
    return 人


def 查询基本信息(RowKey):
    人 = 表服务.get_entity(用户表, 'q', RowKey,
                       select='RowKey, 名字, 大头像, 小头像, 简介, 公开邮箱'
                       )
    return 人


def 写文章(文件类型, 标题, 摘要, 内容, 灵牌):
    from . import 文件存储
    事件uuid = str(uuid.uuid1())
    md5 = 文件存储.上传(内容.encode('utf8'), 'article')
    表服务.insert_entity(事件表, {
        'PartitionKey': 灵牌['RowKey'],
        'RowKey': 事件uuid,
        '时间': time.time(),

        '事件类型': '文章',

        '标题': 标题,
        '摘要': 摘要,
        '文件类型': 文件类型,
        '关联文件': md5,
    })


def 获得推荐用户(灵牌=None):
    所有用户 = 表服务.goku_query_entities(用户表, select='RowKey, 小头像')
    有头像的用户 = [i for i in 所有用户 if i['小头像']]
    取样 = random.sample(有头像的用户, 3)
    return 取样


def 查询用户事件(用户rk):
    事件组 = 表服务.goku_query_entities(事件表, filter=f"PartitionKey eq '{用户rk}'",
                             select='PartitionKey, RowKey, 时间',
                             )
    return 事件组


def 查询事件详细(PartitionKey, RowKey):
    t = 表服务.get_entity(事件表, PartitionKey, RowKey)
    return 表服务.get_entity(事件表, PartitionKey, RowKey)


def 查询事件究极(PartitionKey, RowKey):
    from . import 文件存储
    t = 表服务.get_entity(事件表, PartitionKey, RowKey)
    if t['事件类型'] == '文章':
        t['关联文件内容'] = 文件存储.下载(t['关联文件'], 'article').decode('utf8')
    return t


G = globals()
函数表 = {
    i: f for i, f in G.items()
    if i[0] != '_' and type(f) == types.FunctionType
}


logging.warning(str(函数表))
