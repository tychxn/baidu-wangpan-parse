# 百度网盘分享文件下载链接解析

[![version](https://img.shields.io/badge/python-2.7%2C%203.4%2B-blue.svg)](https://www.python.org) 
[![status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/tychxn/baidu-wangpan-parse)
[![license](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)
[![star, issue](https://img.shields.io/badge/star%2C%20issue-welcome-brightgreen.svg)](https://github.com/tychxn/baidu-wangpan-parse)

## 功能

- 获取百度网盘分享文件的真实下载地址
- 将获取到的下载链接复制到[IDM](http://www.internetdownloadmanager.com/)、[FDM](https://www.freedownloadmanager.org/)等下载器即可实现高速下载，避免使用百度网盘客户端

![](./img/IDM_download.jpg "IDM下载")

## 运行环境

- Python3 (兼容Python2)

## 第三方库

- [Requests](http://docs.python-requests.org/en/master/)
- [tqdm](https://github.com/tqdm/tqdm)

## 使用帮助

```sh
$ python baidu_wangpan_parse.py -h
usage: baidu_wangpan_parse.py [-h] [-f] link [password]

Get Baidu wangpan sharing file download link.

positional arguments:
  link          Baidu wangpan sharing file link
  password      Baidu wangpan sharing file password

optional arguments:
  -h, --help    show this help message and exit
  -f, --folder  if sharing file is a folder
```

## 注意事项

- 【2018.10.16】百度网盘更新，需要用户登陆才能获取下载链接，代码暂时失效，等待后续更新。
- 【2018.10.3】百度网盘最近限制了打包下载，当选择的多个文件大于`300M`时会提示`{"error_code":31090,"error_msg":"package is too large","request_id":8704138921699374750}`。因此无法下载过大的文件夹，单个文件下载不受影响。


## 使用实例

1.获取`没有加密`的`单个文件`的下载地址：
```sh
$ python baidu_wangpan_parse.py https://pan.baidu.com/s/1dG1NCeH
http://d.pcs.baidu.com/file/8192bee674d4fa51327b4fcd48419527?fid=271812880-250528-1043814616287203&dstime=1529692196&rt=sh&sign=FDtAERV-DCb740ccc5511e5e8fedcff06b081203-X4Fh%2FqJm8VsmmFSfxrvr0Xi%2BWuo%3D&expires=8h&chkv=1&chkbd=0&chkpc=&dp-logid=556008995005344418&dp-callid=0&r=913049239
```

2.获取`加密`的`单个文件`的下载地址：
```sh
$ python baidu_wangpan_parse.py https://pan.baidu.com/s/1qZbIVP6 xa27
http://d.pcs.baidu.com/file/db0be336c157d7cd2e1368c7a80833d6?fid=1708072416-250528-674694471059199&dstime=1529692222&rt=sh&sign=FDtAERV-DCb740ccc5511e5e8fedcff06b081203-elkzjwahMSEUGaVYSsBWYDt9y9I%3D&expires=8h&chkv=1&chkbd=0&chkpc=&dp-logid=556015960669176024&dp-callid=0&r=457285671
```

3.获取`没有加密`的`文件夹`的打包下载地址（小于300M）
```sh
$ python baidu_wangpan_parse.py -f https://pan.baidu.com/s/1hIm_wG-LtGPYQ3lY2ANvxQ
https://www.baidupcs.com/rest/2.0/pcs/file?method=batchdownload&app_id=250528&zipcontent=%7B%22fs_id%22%3A%5B%22680498123896117%22%5D%7D&sign=DCb740ccc5511e5e8fedcff06b081203:T%2BfekNxcAnRRurxsKdpdzYxHnDk%3D&uid=1708072416&time=1538662289&dp-logid=8705314671792360782&dp-callid=0&shareid=610414498&from_uk=1708072416
```

4.获取`加密`的`文件夹`的打包下载地址（小于300M）
```sh
$ python baidu_wangpan_parse.py -f https://pan.baidu.com/s/1htWjWk0 5ykw
https://www.baidupcs.com/rest/2.0/pcs/file?method=batchdownload&app_id=250528&zipcontent=%7B%22fs_id%22%3A%5B%22680498123896117%22%5D%7D&sign=DCb740ccc5511e5e8fedcff06b081203:7w%2BgJ2pcVqrLf4AF9rb9N1Z4hDI%3D&uid=1708072416&time=1538661815&dp-logid=8705187263682751022&dp-callid=0&shareid=185984296&from_uk=1708072416
```

## 常见问题

文件打包下载后解压时提示`头部错误`， 解压失败。这个问题多发于`7-Zip`解压，换用`WinRAR`即可解压成功。

## 错误代码

|Errno|含义|
|----|-----|
|0|成功|
|-1|您下载的内容中包含违规信息|
|-20|显示验证码|
|2|下载失败，请稍候重试|
|113|页面已过期|
|116|该分享不存在|
|118|没有下载权限|
|121|你选择操作的文件过多，减点试试吧|

## 待办列表

- 解析文件夹的下载地址同时获取zip压缩包名字以及大小
- ~~精简命令行参数，实现自动识别下载内容是单文件/文件夹，加密/未加密~~
- ~~修改为Python3版本~~

## 备注

- 当前测试时间`2018.10.3`。如果失效，请在issue中提出，我会来更新。
