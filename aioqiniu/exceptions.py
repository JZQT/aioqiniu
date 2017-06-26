# coding: utf-8

import http.client


class HTTPError(Exception):
    """七牛客户端与服务器交互时产生的HTTP错误异常类"""

    def __init__(self, status_code: int, message=None, *args, **kwargs):
        self.status_code = status_code
        self.message = message or http.client.responses.get(status_code, "")

    def __str__(self):
        if self.message:
            return "{} {}".format(self.status_code, self.message)
        return str(self.status_code)

    pass
