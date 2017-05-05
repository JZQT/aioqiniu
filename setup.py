#!/usr/bin/env python3
# coding: utf-8

from setuptools import setup


setup(
    name="aioqiniu",
    version="1.1.0",
    author="JZQT",
    author_email="jzqt@witcoder.com",
    url="https://github.com/JZQT/aioqiniu",
    description="Asynchronous Qiniu Cloud Storage client based on asyncio",
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
