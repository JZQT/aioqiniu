# coding: utf-8

import os
import asyncio

import qiniu
import pytest

from ..tools import (qiniu_environ_is_set_correctly, require_qiniu_environ,
                     get_qiniu_client, get_qiniu_environ)

TEST_BUCKET = 'aioqiniu_test_bucket'


@pytest.mark.incremental
class TestStorageServiceMixin(object):

    def setup(self):
        if qiniu_environ_is_set_correctly():
            ioloop = asyncio.get_event_loop()
            self.qiniu_client = ioloop.run_until_complete(get_qiniu_client())
            self.qiniu = qiniu.Auth(*get_qiniu_environ())

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_create_bucket(self):
        ret = await self.qiniu_client.create_bucket(TEST_BUCKET)
        assert ret is None

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_list_buckets(self):
        buckets = await self.qiniu_client.list_buckets()
        assert TEST_BUCKET in buckets

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_list_domains(self):
        domains = await self.qiniu_client.list_domains(TEST_BUCKET)
        assert len(domains) == 1

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_upload_file(self):
        token = self.qiniu.upload_token(TEST_BUCKET)
        key = os.path.basename(__file__)
        filedata = await self.qiniu_client.upload_file(
            __file__, token, key, mimetype="text/plain")
        assert filedata["key"] == key
        assert filedata["hash"] == qiniu.etag(__file__)
        # 防止上传过快导致无法在bucket里查询出该上传文件的信息
        await asyncio.sleep(5)

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_list_files(self):
        data = await self.qiniu_client.list_files(TEST_BUCKET)
        keys = {filedata["key"] for filedata in data["items"]}
        assert os.path.basename(__file__) in keys

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_get_file_stat(self):
        key = os.path.basename(__file__)
        filestat = await self.qiniu_client.get_file_stat(TEST_BUCKET, key)
        assert filestat is not None and isinstance(filestat, dict)
        assert filestat["mimeType"] == "text/plain"     # 上传时设置的mimetype

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_delete_file_after_days(self):
        ret = await self.qiniu_client.delete_file_after_days(
            TEST_BUCKET, os.path.basename(__file__), 1)
        assert ret is None

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_delete_file(self):
        ret = await self.qiniu_client.delete_file(
            TEST_BUCKET, os.path.basename(__file__))
        assert ret is None

    @require_qiniu_environ
    @pytest.mark.asyncio
    async def test_delete_bucket(self):
        ret = await self.qiniu_client.delete_bucket(TEST_BUCKET)
        assert ret is None

    pass
