# coding: utf-8

import os

import pytest
import aioqiniu

# 七牛AccessKey环境变量名
QINIU_ACCESS_KEY_ENV = "QINIU_ACCESS_KEY"
# 七牛SecretKey环境变量名
QINIU_SECRET_KEY_ENV = "QINIU_SECRET_KEY"

QINIU_ENV_ERROR_MESSAGE = "需要正确设置环境变量'QINIU_ACCESS_KEY'和'QINIU_SECRET_KEY'"


def qiniu_environ_is_set_correctly() -> bool:
    """判断七牛环境变量是否被正确设置"""
    access_key = os.environ.get(QINIU_ACCESS_KEY_ENV, "")
    secret_key = os.environ.get(QINIU_ACCESS_KEY_ENV, "")
    if access_key and secret_key and len(access_key) == len(secret_key):
        return True
    return False


require_qiniu_environ = pytest.mark.skipif(
    not qiniu_environ_is_set_correctly(),
    reason=QINIU_ENV_ERROR_MESSAGE,
)


def get_qiniu_environ() -> tuple:
    """获取用于测试的七牛环境变量

    :return: 返回一个二元组，(QiniuAccessKey, QiniuSecretKey)
    """
    assert qiniu_environ_is_set_correctly(), QINIU_ENV_ERROR_MESSAGE

    return os.environ[QINIU_ACCESS_KEY_ENV], os.environ[QINIU_SECRET_KEY_ENV]


async def get_qiniu_client() -> aioqiniu.QiniuClient:
    """获取一个用于测试的`aioqiniu.QiniuClient`对象

    注意：每次调用函数都会重新生成一个对象
    """
    assert qiniu_environ_is_set_correctly(), QINIU_ENV_ERROR_MESSAGE

    return aioqiniu.QiniuClient(*get_qiniu_environ())
