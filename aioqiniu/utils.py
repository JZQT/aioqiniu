# coding: utf-8

from io import BytesIO
from base64 import urlsafe_b64encode

import qiniu.utils
from aiohttp.client import ClientResponse
from aiohttp.client_exceptions import ContentTypeError

from aioqiniu.exceptions import QiniuError


def get_encoded_entry_uri(bucket: str, key: str = None) -> str:
    """生成七牛云API使用的EncodedEntryURI

    :param bucket: 空间名
    :param key: 文件名，默认为空

    详见：https://developer.qiniu.com/kodo/api/1276/data-format
    """
    entry_uri = "{}:{}".format(bucket, key) if key else bucket
    return urlsafe_b64encode(entry_uri.encode()).decode()


def get_stream_etag(stream) -> str:
    """计算流数据的七牛etag

    :param stream: 流对象，文件对象或类文件对象等

    etag算法详见：https://developer.qiniu.com/kodo/manual/1231/appendix#3
    """
    return qiniu.utils.etag_stream(stream)


def get_bytes_etag(data: bytes) -> str:
    """计算字节数据的七牛etag

    :param data: 字节数据

    etag算法详见：https://developer.qiniu.com/kodo/manual/1231/appendix#3
    """
    return get_stream_etag(BytesIO(data))


def get_file_etag(filepath: str) -> str:
    """计算本地文件的七牛etag

    :param filepath: 本地文件路径

    etag算法详见：https://developer.qiniu.com/kodo/manual/1231/appendix#3
    """
    return qiniu.utils.etag(filepath)


async def raise_for_error(response: ClientResponse):
    if response.status < 300:
        return
    try:
        value = await response.json()
        raise QiniuError(code=value['code'], error=value['error'])
    except QiniuError:
        raise
    except (KeyError, TypeError, ContentTypeError):
        response.raise_for_status()
