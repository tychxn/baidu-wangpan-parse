# 百度网盘私密分享下载链接解析
## 功能
- 获取百度网盘分享文件的真实下载链接。
- 将获取到的下载链接复制到[IDM](http://www.internetdownloadmanager.com/)、[FDM](http://www.internetdownloadmanager.com/)等下载器即可实现高速下载，避免使用百度网盘客户端。

## 环境
- Python 2.7

## 使用帮助
```sh
$ python baidu_wangpan_parse.py -h
usage: baidu_wangpan_parse.py [-h] -l LINK -p PASSWORD

Get Baidu wangpan private sharing file download link.

optional arguments:
  -h, --help            show this help message and exit
  -l LINK, --link LINK  Baidu wangpan sharing file link
  -p PASSWORD, --password PASSWORD
                        Baidu wangpan sharing file password
```

## 备注
- 只能解析私密分享文件（带密码）的下载地址
- 只能解析单个分享的文件下载地址，不能解析文件夹下载地址
