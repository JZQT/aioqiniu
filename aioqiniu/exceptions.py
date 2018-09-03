# coding: utf-8


class QiniuError(Exception):
    """七牛的接口错误异常

    详见：https://developer.qiniu.com/kodo/api/3928/error-responses
    """
    def __init__(self, code: int, error: str):
        self.code = code
        self.error = error

    def __str__(self):
        return f'QiniuError(code={self.code:r}, error={self.error:r})'

    def __repr__(self):
        return self.__str__()
