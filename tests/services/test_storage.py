# coding: utf-8

import asyncio

import pytest

from ..tools import (qiniu_environ_is_set_correctly, require_qiniu_environ,
                     get_qiniu_client)

TEST_BUCKET = 'aioqiniu_test_bucket'


class TestStorageServiceMixin(object):

    def setup(self):
        if qiniu_environ_is_set_correctly():
            ioloop = asyncio.new_event_loop()
            self.qiniu_client = ioloop.run_until_complete(get_qiniu_client())

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
    async def test_delete_bucket(self):
        ret = await self.qiniu_client.delete_bucket(TEST_BUCKET)
        assert ret is None

    pass
