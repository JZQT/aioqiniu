# aioqiniu

![][version] ![][license] ![][python]

`aioqiniu`是基于`aiohttp`的七牛云Python异步客户端库。

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

[version]: https://img.shields.io/badge/version-0.1.0-blue.svg
[license]: https://img.shields.io/badge/license-MIT-blue.svg
[python]: https://img.shields.io/badge/python-%3E%3D3.5-blue.svg
