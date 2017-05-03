#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup


setup(
    name="aioqiniu",
    author="JZQT",
    url="https://github.com/JZQT/aioqiniu",
    author_email="jzqt@witcoder.com",
    version="1.0.0",
    description="Asynchronous Qiniu Cloud Storage client based on aiohttp",
    install_requires=['qiniu', 'aiohttp'],
    packages=['aioqiniu'],
    license="MIT",
    keywords="qiniu asyncio",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)