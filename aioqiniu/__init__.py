# coding: utf-8

from urllib.parse import urlencode

import qiniu
import aiohttp

from aioqiniu.services import StorageServiceMixin
from aioqiniu.exceptions import HTTPError       # noqa: F401

__version__ = "1.2.0"


class QiniuClient(StorageServiceMixin):
    """七牛云存储异步客户端"""

    def __init__(self, access_key: str, secret_key: str, httpclient=None):
        """初始化七牛云异步客户端

        :param access_key: 七牛云的AccessKey
        :param secret_key: 七牛云的SecretKey
        :param httpclient: 自定义`aiohttp.ClientSession`对象，默认为空，自动创建
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self._auth = qiniu.Auth(access_key, secret_key)
        self._auto_close_httpclient = False
        if httpclient is None:
            httpclient = aiohttp.ClientSession()
            self._auto_close_httpclient = True
        self._httpclient = httpclient

    def get_token(self, data: str):
        """从原始数据中生成的token

        该方法等同于`qiniu.Auth.token`

        :param data: 待签名数据

        :return: 数据签名
        """
        return self._auth.token(data)

    def get_token_with_data(self, data: str):
        """生成带原始数据的token

        该方法等同于`qiniu.Auth.token_with_data`

        :param data: 待签名数据

        :return: 数据签名，含已编码的原数据
        """
        return self._auth.token_with_data(data)

    def get_access_token(self, path: str, query="", body="") -> str:
        """生成七牛云的管理凭证(access token)

        :param path: URL路径
        :param query: URL查询字符串，可以是str或dict类型，默认为空
        :param body: 请求body，默认为空

        :return: 七牛云的管理凭证(access token)

        详见：https://developer.qiniu.com/kodo/manual/1201/access-token
        """
        if not query:
            return self._auth.token("{}\n{}".format(path, body))
        if isinstance(query, dict):
            query = urlencode(query)
        return self._auth.token("{}?{}\n{}".format(path, query, body))

    def get_upload_token(self, bucket: str, key=None, expires=3600,
                         policy=None, strict_policy=True) -> str:
        """生成七牛云的上传凭证(upload token)

        :param bucket: 空间名
        :param key: 上传的文件命名，默认为空
        :param expires: 上传凭证过期时间，单位为秒，默认为3600
        :param policy: 上传策略，默认为空

        :return: 七牛云的上传凭证(upload token)

        详见：https://developer.qiniu.com/kodo/manual/1208/upload-token
        """
        return self._auth.upload_token(bucket, key, expires, policy,
                                       strict_policy)

    def get_private_download_url(self, url, expires=3600) -> str:
        """生成私有资源的下载url

        :param url: 私有资源的url
        :param expires: 下载url的过期时间，单位为秒，默认为3600

        :return: 私有资源的下载url

        详见：https://developer.qiniu.com/kodo/manual/1202/download-token
        """
        return self._auth.private_download_url(url, expires)

    def __del__(self):
        if self._auto_close_httpclient:
            self._httpclient.close()

    pass
