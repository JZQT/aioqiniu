# coding: utf-8

import asyncio
from random import random, randint

import qiniu

from .tools import (qiniu_environ_is_set_correctly, require_qiniu_environ,
                    get_qiniu_client, get_qiniu_environ)


class TestQiniuClient(object):

    def setup(self):
        if qiniu_environ_is_set_correctly():
            ioloop = asyncio.new_event_loop()
            self.qiniu_client = ioloop.run_until_complete(get_qiniu_client())
            self.qiniu_auth = qiniu.Auth(*get_qiniu_environ())

    @require_qiniu_environ
    def test_get_token(self):
        for i in range(10):
            data = str(random())
            answer = self.qiniu_auth.token(data)
            assert self.qiniu_client.get_token(data) == answer

    @require_qiniu_environ
    def test_get_token_with_data(self):
        for i in range(10):
            data = str(random())
            answer = self.qiniu_auth.token_with_data(data)
            assert self.qiniu_client.get_token_with_data(data) == answer

    @require_qiniu_environ
    def test_get_upload_token(self):
        args_list = [('bucket', ), ('bucket', 'key'), ('bucket', 'key', 1)]
        for args in args_list:
            answer = self.qiniu_auth.upload_token(*args)
            assert self.qiniu_client.get_upload_token(*args) == answer

    @require_qiniu_environ
    def test_get_private_download_url(self):
        for i in range(10):
            args = (str(random()), randint(1, 1000000))
            answer = self.qiniu_auth.private_download_url(*args)
            assert self.qiniu_client.get_private_download_url(*args) == answer

    pass
