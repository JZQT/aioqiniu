# aioqiniu

[![][qiniu_logo]](https://www.qiniu.com)

![][version] ![][license] ![][python]

`aioqiniu`是基于`asyncio`和`aiohttp`的七牛云Python异步客户端库。

## Install

```bash
$ sudo pip3 install aioqiniu
```

## Requirements

* Python &gt;= 3.5
* qiniu
* aiohttp &gt;= 3.4.0

## Getting started

使用样例：获取文件元信息

```python
import asyncio

import aioqiniu


async def main():
    async with aioqiniu.QiniuClient("MY_ACCESS_KEY", "MY_SECRET_KEY") as client:
        stat = await client.get_file_stat("BUCKET_NAME", "FILE_NAME")
        print(stat)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

## Documentation

直接在Python中通过`help`来查看`aioqiniu`的API文档。

更多API细节可查看注释中提供的七牛官方文档地址。

## Tests

本项目使用`pytest`做单元测试，运行测试需要安装以下依赖

* `pytest`
* `pytest-asyncio`
* `pytest-incremental`

运行下面的命令安装运行测试所需的依赖

```bash
$ sudo pip3 install pytest pytest-asyncio pytest-incremental
```

在该项目根目录下执行以下命令来运行测试

```bash
$ pytest
```

**注意**：部分测试需要设置环境变量`QINIU_ACCESS_KEY`和`QINIU_SECRET_KEY`才会运行

## Changelog

* `v1.3.0`(2018-09-04)

    * `QiniuClient` 的初始化参数 `client` 更改为 `httpclient`
    * `QiniuClient` 的 `upload_data` 和 `upload_file` 方法添加 `mimetype` 参数
    * 添加新模块 `aioqiniu.exceptions`，包含异常类 `QiniuError`，作为与七牛服务器交互产生的业务异常
    * 完善类型注释
    * 现在可以通过 `.httpclient` 来访问 `QiniuClient` 所使用的 `aiohttp.client.ClientSession` 的对象
    * 添加 `close`, `__aenter__` 以及 `__aexit__` 等方法，现在可以像类似 aiohttp 的 `ClientSession` 一样关闭 `QiniuClient`

        ```python
        async with QiniuClient() as client:
            # do something
            pass
        ```

        ```python
        async def use_qiniu_client():
            client = QiniuClient()
            # do something
            await client.close()
        ```
    * 修复 `QiniuClient.rename_file` 方法不可用的 bug

* `v1.2.0`(2017-05-10)

    * `aioqiniu.utils`模块添加计算七牛etag相关的工具函数

        * `get_stream_etag`

            从一个流中读取数据并计算七牛etag

        * `get_data_etag`

            从字节码数据中计算七牛etag

        * `get_file_etag`

            从本地文件中读取数据计算七牛etag

    * `QiniuClient`添加从原始数据中计算token的一些相关方法，用于替代`qiniu.Auth`的相关功能

        * `get_token`

            根据原始数据生成token，同`qiniu.Auth.token`

        * `get_token_with_data`

            根据原始数据生成含已编码原始数据的token，同`qiniu.Auth.token_with_data`

    * 添加生成私有资源url的方法`QiniuClient.get_private_download_url`

* `v1.1.0`(2017-05-05)

    * API`QiniuClient.get_encoded_entry_uri`转移到新模块`aioqiniu.utils`中作为一个函数来使用

    * 添加批量操作的API`QiniuClient.batch`

    * 添加直传本地文件的API`QiniuClient.upload_file`

    * 更改`QiniuClient.upload_data`方法的参数名，使API调用更加方便

        * `upload_token -> token`
        * `upload_host -> host`

    * 更换`QiniuClient.upload_data`API的`data`和`token`的参数位置，调用更符合直觉，现在是这样调用

        ```python
        await qiniuclient.upload_data(data, token, ...)
        ```

* `v1.0.0`(2017-05-03)

    基于`asyncio`和`aiohttp`的七牛云Python异步客户端库。

    支持以下API：

    * 查询、创建和删除空间
    * 查询空间绑定的域名列表
    * 查找、上传和删除文件
    * 拷贝、移动和重命名文件
    * 修改文件MIME类型信息
    * 设置文件的生命周期
    * 镜像回源预取
    * 第三方资源抓取
    * 其它主要是内部使用的API（非协程API，主要是生成token以及相关的数据格式）

[qiniu_logo]: http://assets.qiniu.com/qiniu-204x109.png
[version]: https://img.shields.io/badge/version-1.3.0-blue.svg
[license]: https://img.shields.io/badge/license-MIT-blue.svg
[python]: https://img.shields.io/badge/python-%3E%3D3.5-blue.svg
