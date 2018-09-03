# coding: utf-8

from typing import Union
from urllib.parse import urlencode

import qiniu
from aiohttp.client import ClientSession

from aioqiniu.services import StorageServiceMixin

__version__ = "1.3.0"


class QiniuClient(StorageServiceMixin):
    """七牛云存储异步客户端"""

    def __init__(self, access_key: str, secret_key: str, httpclient: ClientSession = None):
        """初始化七牛云异步客户端

        :param access_key: 七牛云 AccessKey
        :param secret_key: 七牛云 SecretKey
        :param httpclient: 自定义 `aiohttp.client.ClientSession` 对象，默认为空，自动创建
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self._auth = qiniu.Auth(access_key, secret_key)
        if httpclient is None:
            httpclient = ClientSession()
        self.httpclient = httpclient

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self) -> None:
        await self.httpclient.close()

    @property
    def closed(self) -> bool:
        return self.httpclient.closed

    def get_token(self, data: str) -> str:
        """从原始数据中生成的token

        该方法等同于`qiniu.Auth.token`

        :param data: 待签名数据

        :return: 数据签名
        """
        return self._auth.token(data)

    def get_token_with_data(self, data: str) -> str:
        """生成带原始数据的token

        该方法等同于`qiniu.Auth.token_with_data`

        :param data: 待签名数据

        :return: 数据签名，含已编码的原数据
        """
        return self._auth.token_with_data(data)

    def get_access_token(self, path: str, query: Union[str, dict] = "", body: str = "") -> str:
        """生成七牛云的管理凭证(access token)

        :param path: URL 路径
        :param query: URL 查询字符串，可以是 str 或 dict 类型
        :param body: 请求 body

        :return: 七牛云的管理凭证(access token)

        详见：https://developer.qiniu.com/kodo/manual/1201/access-token
        """
        if not query:
            return self._auth.token("{}\n{}".format(path, body))
        if isinstance(query, dict):
            query = urlencode(query)
        return self._auth.token("{}?{}\n{}".format(path, query, body))

    def get_upload_token(self, bucket: str, key: str = None, expires: int = 3600,
                         policy=None, strict_policy: bool = True) -> str:
        """生成七牛云的上传凭证(upload token)

        :param bucket: 空间名
        :param key: 上传的文件命名，默认为空
        :param expires: 上传凭证过期时间，单位为秒，默认为3600
        :param policy: 上传策略，默认为空

        :return: 七牛云的上传凭证(upload token)

        详见：https://developer.qiniu.com/kodo/manual/1208/upload-token
        """
        return self._auth.upload_token(
            bucket, key, expires, policy, strict_policy
        )

    def get_private_download_url(self, url: str, expires: int = 3600) -> str:
        """生成私有资源的下载 URL

        :param url: 私有资源的 URL
        :param expires: 下载 URL 的过期时间，单位为秒，默认为 3600

        :return: 私有资源的下载 URL

        详见：https://developer.qiniu.com/kodo/manual/1202/download-token
        """
        return self._auth.private_download_url(url, expires)
