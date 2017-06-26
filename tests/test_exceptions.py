# coding: utf-8

from http.client import responses

from aioqiniu.exceptions import HTTPError


class TestHTTPError(object):

    def test_raise_httperror(self):
        try:
            raise HTTPError(500)
        except HTTPError as e:
            assert e.status_code == 500
            assert e.message == "Internal Server Error"

        try:
            raise HTTPError(404, "Page Not Found")
        except Exception as e:
            assert e.status_code == 404
            assert e.message == "Page Not Found"

    def test_httperror_reason(self):
        for status_code, reason in responses.items():
            if status_code < 400:
                continue
            assert HTTPError(status_code).message == reason

    def test_httperror_str(self):
        assert str(HTTPError(404, "Page Not Found")) == "404 Page Not Found"
        assert str(HTTPError(400)) == "400 Bad Request"
        assert str(HTTPError(100000)) == "100000"

    pass
