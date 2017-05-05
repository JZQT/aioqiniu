# coding: utf-8

import os
from io import BytesIO
from urllib.parse import urlencode
from base64 import b32encode, urlsafe_b64encode

import qiniu
import aiohttp

from aioqiniu.utils import get_encoded_entry_uri

__version__ = "1.1.0"


class QiniuClient(object):
    """七牛云存储异步客户端"""

    _opcode2arglen = {
        "stat": (2, ),
        "copy": (4, 5),
        "move": (4, 5),
        "rename": (3, 4),
        "delete": (2, ),
    }

    def __init__(self, access_key: str, secret_key: str, client=None):
        """初始化七牛云异步客户端

        :param access_key: 七牛云的AccessKey
        :param secret_key: 七牛云的SecretKey
        :param client: 自定义`aiohttp.ClientSession`对象，默认为空，自动创建
        """
        self.__access_key = access_key
        self.__secret_key = secret_key
        self._auth = qiniu.Auth(access_key, secret_key)
        self._auto_close_client = False
        if client is None:
            client = aiohttp.ClientSession()
            self._auto_close_client = True
        self._client = client

    def get_access_token(self, path: str, query="", body="") -> str:
        """生成七牛云的管理凭证

        :param path: URL路径
        :param query: URL查询字符串，可以是str或dict类型，默认为空
        :param body: 请求body，默认为空

        详见：https://developer.qiniu.com/kodo/manual/1201/access-token
        """
        if not query:
            return self._auth.token("{}\n{}".format(path, body))
        if isinstance(query, dict):
            query = urlencode(query)
        return self._auth.token("{}?{}\n{}".format(path, query, body))

    def get_upload_token(self, bucket: str, key=None, expires=3600,
                         policy=None, strict_policy=True) -> str:
        """生成七牛云的上传凭证

        :param bucket: 空间名
        :param key: 上传的文件命名，默认为空
        :param expires: 上传凭证过期时间，单位为秒，默认为3600
        :param policy: 上传策略，默认为空

        详见：https://developer.qiniu.com/kodo/manual/1208/upload-token
        """
        return self._auth.upload_token(bucket, key, expires, policy,
                                       strict_policy)

    async def create_bucket(self, bucket: str, region=None, g=False) -> None:
        """创建空间

        :param bucket: 待创建空间名
        :param region: 待创建空间的存储区域，默认为"z0"表示华东，"z1"是华北
        :param g: global标记，默认为False

        注意：谨慎使用，建议到七牛开发者平台进行操作。

        详见：https://developer.qiniu.com/kodo/api/1382/mkbucketv2
        """
        encoded_bucket = urlsafe_b64encode(bucket.encode()).decode()
        region = region or "z0"
        g = "true" if g else "false"
        path = "/mkbucketv2/{}/region/{}/global/{}".format(
            encoded_bucket, region, g)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def delete_bucket(self, bucket: str) -> None:
        """删除空间

        :param bucket: 待删除空间名

        注意：谨慎使用，建议到七牛开发者平台进行操作。

        详见：https://developer.qiniu.com/kodo/api/1601/drop-bucket
        """
        access_token = self.get_access_token("/drop/{}".format(bucket))
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com/drop/{}".format(bucket)

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def list_buckets(self) -> list:
        """列举该账户下的所有空间名

        详见：https://developer.qiniu.com/kodo/api/1613/user-buckets
        """
        access_token = self.get_access_token("/buckets")
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "https://rs.qbox.me/buckets"

        async with self._client.get(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)
            bucket_list = await resp.json()

        return bucket_list

    async def list_domains(self, bucket: str) -> list:
        """列举指定存储空间绑定的域名列表

        :param bucket: 空间名

        详见：https://developer.qiniu.com/kodo/api/1612/bucket-domainlist
        """
        querystring = urlencode({"tbl": bucket})
        access_token = self.get_access_token("/v6/domain/list", querystring)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "https://api.qiniu.com/v6/domain/list?{}".format(querystring)

        async with self._client.get(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)
            domain_list = await resp.json()

        return domain_list

    async def list_files(self, bucket: str, limit=1000, prefix=None,
                         delimiter=None, marker=None) -> dict:
        """列举文件

        :param bucket: 待列举文件空间名
        :param limit: 列举的条目数，取值范围[1, 1000]，默认1000
        :param prefix: 指定文件的前缀，默认为空
        :param delimiter: 指定目录分隔符，会模拟目录的列出效果，默认为空
        :param marker: 上一次列举返回的标记，作为本次列举的起点，默认为空

        详见：https://developer.qiniu.com/kodo/api/1284/list
        """
        querystring = urlencode({
            "bucket": bucket, "limit": limit, "prefix": prefix or "",
            "delimiter": delimiter or "", "marker": marker or ""})
        access_token = self.get_access_token("/list", querystring)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "https://rsf.qbox.me/list?{}".format(querystring)

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)
            files = await resp.json()

        return files

    async def copy_file(self, bucket: str, key: str, to_bucket: str,
                        to_key: str, force=False) -> None:
        """拷贝文件

        :param bucket: 待拷贝文件空间名
        :param key: 待拷贝文件名
        :param to_bucket: 目标空间名
        :param to_key: 目标文件名
        :param force: force标记，bool类型，默认为False

        详见：https://developer.qiniu.com/kodo/api/1254/copy
        """
        src_encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        dst_encoded_entry_uri = get_encoded_entry_uri(to_bucket, to_key)
        path = "/copy/{}/{}/force/{}".format(
            src_encoded_entry_uri, dst_encoded_entry_uri,
            "true" if force else "false")
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def delete_file(self, bucket: str, key: str) -> None:
        """删除文件

        :param bucket: 待删除文件所在空间名
        :param key: 待删除文件名

        详见：https://developer.qiniu.com/kodo/api/1257/delete
        """
        encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        path = "/delete/{}".format(encoded_entry_uri)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def move_file(self, bucket: str, key: str, to_bucket: str,
                        to_key: str, force=False) -> None:
        """移动文件

        :param bucket: 待移动文件空间名
        :param key: 待移动文件名
        :param to_bucket: 目标空间名
        :param to_key: 目标文件名
        :param force: force标记，bool类型，默认为False

        详见：https://developer.qiniu.com/kodo/api/1288/move
        """
        src_encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        dst_encoded_entry_uri = get_encoded_entry_uri(to_bucket, to_key)
        path = "/move/{}/{}/force/{}".format(
            src_encoded_entry_uri, dst_encoded_entry_uri,
            "true" if force else "false")
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def rename_file(self, bucket: str, key: str, to_key: str,
                          force=False) -> None:
        """重命名文件

        本质上是调用移动文件功能来实现。

        :param bucket: 待重命名文件所在空间
        :param key: 待重命名文件名
        :param to_key: 目标文件名
        :param force: force标记，bool类型，默认为False

        详见：https://developer.qiniu.com/kodo/api/1288/move
        """
        return await self.move(bucket, key, bucket, to_key, force)

    async def get_file_stat(self, bucket: str, key: str) -> dict:
        """查询文件信息

        :param bucket: 待查询文件空间名
        :param key: 待查询文件名

        详见：https://developer.qiniu.com/kodo/api/1308/stat
        """
        encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        path = "/stat/{}".format(encoded_entry_uri)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.get(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)
            stat = await resp.json()

        return stat

    async def change_file_mime(self, bucket: str, key: str, mime: str) -> None:
        """修改文件的MIME类型信息

        :param bucket: 待操作资源所在空间名
        :param key: 待操作资源文件名
        :param mime: 待操作文件目标MIME类型信息

        详见：https://developer.qiniu.com/kodo/api/1252/chgm
        """
        encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        encoded_mime = urlsafe_b64encode(mime.encode()).decode()
        path = "/chgm/{}/mime/{}".format(encoded_entry_uri, encoded_mime)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def delete_file_after_days(self, bucket: str, key: str,
                                     days: int) -> None:
        """设置文件在指定天数后删除

        :param bucket: 待设置文件所在空间名
        :param key: 待设置文件名
        :param days: 文件存活的天数，设置为0表示无限存活期

        详见：https://developer.qiniu.com/kodo/api/1732/update-file-lifecycle
        """
        encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        path = "/deleteAfterDays/{}/{}".format(encoded_entry_uri, days)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def upload_data(self, data: bytes, token: str, key=None, params=None,
                          filename=None, host=None) -> dict:
        """直传文件数据到七牛云

        :param data: 上传的字节码数据
        :param token: 上传凭证
        :param key: 上传后的文件命名
        :param params: 用户自定义参数，可为空，dict类型
        :param filename: 上传的数据的文件名，默认为空
        :param host: 上传的服务器地址，默认为"upload.qiniu.com"

        详见：https://developer.qiniu.com/kodo/api/1312/upload
        """
        filename = filename or b32encode(os.urandom(5)).decode()
        params = params or {}
        host = host or "http://upload.qiniu.com"
        if host.startswith("http://") or host.startswith("https://"):
            url = host
        else:
            url = "http://{}".format(host)

        with aiohttp.MultipartWriter("form-data") as mpwriter:
            mpwriter.append(token, {
                "Content-Disposition": 'form-data; name="token"',
            })
            mpwriter.append(key, {
                "Content-Disposition": 'form-data; name="key"',
            })
            for name, value in params.items():
                mpwriter.append(value, {
                    "Content-Disposition": 'form-data; name="{}"'.format(name),
                })
            mpwriter.append(BytesIO(data), {
                "Content-Disposition":
                    'form-data; name="file"; filename="{}"'.format(filename),
                "Content-Transfer-Encoding": "binary",
            })

        async with self._client.post(url, data=mpwriter) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)
            ret = await resp.json()

        return ret

    async def upload_file(self, filepath: str, token: str, key=None,
                          params=None, host=None) -> dict:
        """直传本地文件到七牛云

        :param filepath: 待上传的文件路径
        :param token: 上传凭证
        :param key: 上传后的文件命名
        :param params: 用户自定义参数，可为空，dict类型
        :param host: 上传的服务器地址，默认为"upload.qiniu.com"

        详见：https://developer.qiniu.com/kodo/api/1312/upload
        """
        with open(filepath, "rb") as f:
            data = f.read()
        filename = os.path.basename(filepath)
        return await self.upload_data(
            data=data, token=token, key=key, params=params,
            filename=filename, host=host)

    async def prefetch(self, bucket: str, key: str) -> None:
        """镜像回源预取

        对于设置了镜像存储的空间，从镜像源站抓取指定资源并存储到该空间中。
        如果该空间中已存在同名资源，则会将镜像源站的资源覆盖空间中的同名资源。

        :param bucket: 待获取资源的镜像空间名
        :param key: 待获取资源文件名

        详见：https://developer.qiniu.com/kodo/api/1293/prefetch
        """
        encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        path = "/prefetch/{}".format(encoded_entry_uri)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "https://iovip.qbox.me" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)

        return

    async def fetch(self, url: str, bucket: str, key=None) -> dict:
        """七牛云第三方资源抓取

        :param url: 要抓取的URL
        :param bucket: 目标资源空间名
        :param key: 目标资源文件名，默认为空

        详见：https://developer.qiniu.com/kodo/api/1263/fetch
        """
        encoded_url = urlsafe_b64encode(url.encode()).decode()
        encoded_entry_uri = get_encoded_entry_uri(bucket, key)
        path = "/fetch/{}/to/{}".format(encoded_url, encoded_entry_uri)
        access_token = self.get_access_token(path)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "https://iovip.qbox.me" + path

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status == 200, "HTTP {}".format(resp.status)
            ret = await resp.json()

        return ret

    async def batch(self, *operations) -> list:
        """批量操作

        支持的批量操作的操作类型：

        * 查询文件信息，操作码"stat"
        * 拷贝文件，操作码"copy"
        * 移动文件，操作码"move"
        * 重命名文件，操作码"rename"
        * 删除文件，操作码"delete"

        用操作元组来描述一个操作，操作元组的第一个元素是操作码，
        之后的元组元素为对应方法的参数。下面是有效的操作元组示例：

            ("stat", "BUCKET", "KEY")
            ("copy", "BUCKET", "KEY", "TO_BUCKET", "TO_KEY", True)
            ("move", "BUCKET", "KEY", "TO_BUCKET", "TO_KEY")
            ("rename", "BUCKET", "KEY", "TO_KEY", True)
            ("delete", "BUCKET", "KEY")

        :param *operations: 变长位置参数，元素为操作元组

        详见：https://developer.qiniu.com/kodo/api/1250/batch
        """
        querystring = "&".join(
            [self._get_operation_string(op[0], *op[1:]) for op in operations]
        )
        access_token = self.get_access_token("/batch", querystring)
        headers = {"Authorization": "QBox {}".format(access_token)}
        url = "http://rs.qiniu.com/batch?" + querystring

        async with self._client.post(url, headers=headers) as resp:
            assert resp.status < 400, "HTTP {}".format(resp.status)
            ret = await resp.json()

        return ret

    def _get_operation_string(self, code: str, *args) -> str:
        assert code in self._opcode2arglen, "非法的操作码: {}".format(code)
        assert len(args) in self._opcode2arglen[code], "操作参数错误"

        if code in ("stat", "delete"):
            return "op=/{}/{}".format(code, get_encoded_entry_uri(*args))
        if code == "rename":
            code = "move"
            args = (*args[:2], args[0], *args[2:])
        if code in ("move", "copy"):
            src = get_encoded_entry_uri(args[0], args[1])
            dst = get_encoded_entry_uri(args[2], args[3])
            force = "true" if len(args) == 5 and args[4] else "false"
            return "op=/{}/{}/{}/force/{}".format(code, src, dst, force)

    def __del__(self):
        if self._auto_close_client:
            self._client.close()

    pass
