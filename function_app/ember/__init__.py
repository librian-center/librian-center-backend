import logging
import json
import inspect

import azure.functions as func
from azure.common import AzureHttpError

from .utils import 莉沫Error, 错误简化
from . import 接口


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        return 分配器(req)
    except AzureHttpError as e:
        logging.exception(e)
        return response(f'Azure错误: {错误简化(e)}', status_code=e.status_code)
    except AssertionError as e:
        logging.exception(e)
        return response(f'验证错误: {错误简化(e)}', status_code=422)
    except 莉沫Error as e:
        logging.exception(e)
        return response(f'莉沫错误: {错误简化(e)}', status_code=422)
    except Exception as e:
        logging.exception(e)
        return response(f'运行错误: {错误简化(e)}', status_code=500)


def response(x, status_code=200):
    新x = json.dumps(x, ensure_ascii=False)
    return func.HttpResponse(新x, status_code=status_code)


def 提取参数(req: func.HttpRequest) -> dict:
    参数表 = dict(req.params)
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        参数表.update(req_body)
    return 参数表


def 分配器(req: func.HttpRequest) -> func.HttpResponse:
    参数表 = 提取参数(req)
    if 'code' in 参数表:
        del 参数表['code']
    assert 'f' in 参数表, '你得指定函数名。'
    函数名 = 参数表['f']
    del 参数表['f']
    assert 函数名 in 接口.函数表, f'「{函数名}」不能调用。'
    函数 = 接口.函数表[函数名]
    if '灵牌' in 参数表: 
        if '灵牌' not in inspect.getargspec(函数).args: 
            del 参数表['灵牌']
        else:
            assert 接口._灵牌验证(参数表['灵牌']), '灵牌无效。'
    运行结果 = 函数(**参数表)
    return response(运行结果)
