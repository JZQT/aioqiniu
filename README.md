# aioqiniu

![][qiniu]

![][version] ![][license] ![][python]

`aioqiniu`是基于`asyncio`和`aiohttp`的七牛云Python异步客户端库。

## Install

```bash
$ sudo pip3 install aioqiniu
```

## Requirements

* Python &gt;= 3.5
* qiniu
* aiohttp

## Getting started

使用样例：获取文件元信息

```python
import asyncio

import aioqiniu

async def main():
    client = aioqiniu.QiniuClient("MY_ACCESS_KEY", "MY_SECRET_KEY")
    stat = await client.get_file_stat("BUCKET_NAME", "FILE_NAME")
    print(stat)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
```

## Documentation

直接在Python中通过`help`来查看`aioqiniu`的API文档。

更多API细节可查看注释中提供的七牛官方文档地址。

## Changelogs

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

[qiniu]: http://assets.qiniu.com/qiniu-204x109.png
[version]: https://img.shields.io/badge/version-1.0.0-blue.svg
[license]: https://img.shields.io/badge/license-MIT-blue.svg
[python]: https://img.shields.io/badge/python-%3E%3D3.5-blue.svg
