#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup

import aioqiniu


setup(
    name="aioqiniu",
    author="JZQT",
    url="https://github.com/JZQT/aioqiniu",
    author_email="jzqt@witcoder.com",
    version=aioqiniu.__version__,
    description="Asynchronous Qiniu Cloud Storage client based on aiohttp",
    install_requires=['qiniu', 'aiohttp'],
    license="MIT",
    keywords="qiniu asyncio",
)
