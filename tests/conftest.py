# coding: utf-8

import pytest


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        if call.excinfo is not None:
            parent = item.parent
            parent._prev_test_failed = item


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        prev_test_failed = getattr(item.parent, "_prev_test_failed", None)
        if prev_test_failed is not None:
            test_name = prev_test_failed.name
            pytest.skip("前置测试未成功运行 ({})".format(test_name))
