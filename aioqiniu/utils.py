# coding: utf-8

from base64 import urlsafe_b64encode


def get_encoded_entry_uri(bucket: str, key=None) -> str:
    """生成七牛云API使用的EncodedEntryURI

    :param bucket: 空间名
    :param key: 文件名，默认为空

    详见：https://developer.qiniu.com/kodo/api/1276/data-format
    """
    entry_uri = "{}:{}".format(bucket, key) if key else bucket
    return urlsafe_b64encode(entry_uri.encode()).decode()
