# coding: utf-8

import os
from io import BytesIO
from random import choice, randint
from string import ascii_letters

import qiniu.utils as qutils
import aioqiniu.utils as aqutils


def test_get_encoded_entry_uri():
    for i in range(20):
        bucket = ''.join(choice(ascii_letters) for i in range(10))
        key = ''.join(choice(ascii_letters) for i in range(10))
        assert aqutils.get_encoded_entry_uri(
            bucket, key) == qutils.entry(bucket, key)


def test_get_stream_etag():
    assert aqutils.get_stream_etag(
        BytesIO(b'')) == qutils.etag_stream(BytesIO(b''))

    for i in range(10):
        data = os.urandom(randint(1, 2 * 4 * 1024 * 1024))
        assert aqutils.get_stream_etag(
            BytesIO(data)) == qutils.etag_stream(BytesIO(data))


def test_get_bytes_etag():
    assert aqutils.get_bytes_etag(b'') == qutils.etag_stream(BytesIO(b''))

    for i in range(10):
        data = os.urandom(randint(1, 2 * 4 * 1024 * 1024))
        assert aqutils.get_bytes_etag(
            data) == qutils.etag_stream(BytesIO(data))


def test_get_file_etag():
    assert aqutils.get_file_etag(__file__) == qutils.etag(__file__)
