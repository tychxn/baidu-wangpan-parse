#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    python解析百度云私密分享文件下载链接
    （只能解析单个私密文件下载地址，不能解析文件夹下载地址）
    基于python2.7
'''

import requests
import re
import time
import json
import random
import os
import urllib


class BaiduParser(object):

    def __init__(self):
        self.sess = requests.Session()

        self.primaryid = ""
        self.uk = ""
        self.sign = ""
        self.timestamp = ""
        self.fid_list = ""
        self.vcode_str = ""
        self.vcode_input = ""
        self.extra = ""

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'Host': 'pan.baidu.com',
            'Origin': 'https://pan.baidu.com'
        }

    def get_baidu_cookie(self):    # 初始化cookie
        url = 'http://pan.baidu.com'
        self.sess.get(url, headers=self.headers)

    def verify_pwd(self, link, pwd):  # post文件密码用于验证
        verify_url = 'https://pan.baidu.com/share/verify'

        match = re.match(r'http[s]?://pan.baidu.com/s/1(.*)', link)
        if not match:
            print u'link match error!'
            return False
        surl = match.group(1)

        payload = {
            'surl': surl,
            't': '%d' % (time.time() * 1000),
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
        }

        data = {
            'pwd': pwd,
            'vcode': '',
            'vcode_str': '',
        }

        self.headers['Referer'] = link;

        resp = self.sess.post(verify_url, data=data, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        if js['errno'] == 0:
            return True
        else:
            return False

    def get_params(self, link):  # 重新载入页面来获取后面所需的参数
        resp = self.sess.get(link, headers=self.headers)
        resp.encoding = 'utf-8'

        # 读取页面中的参数
        m = re.search('\"sign\":\"(.+?)\"', resp.text)
        self.sign = m.group(1)
        m = re.search('\"timestamp\":(.+?),\"', resp.text)
        self.timestamp = m.group(1)
        m = re.search('\"shareid\":(.+?),\"', resp.text)
        self.primaryid = m.group(1)
        m = re.search('\"uk\":(.+?),\"', resp.text)
        self.uk = m.group(1)
        m = re.search('\"fs_id\":(.+?),\"', resp.text)
        self.fid_list = '[' + m.group(1) + ']'

    def get_vcode(self, link):  # 获取验证码并要求输入
        vcode_str_url = "http://pan.baidu.com/api/getvcode"
        payload = {
            'prod': 'pan',
            't': random.random(),
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
        }

        resp = self.sess.get(vcode_str_url, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        self.vcode_str = js['vcode']

        # 保存验证码
        img_url = "http://pan.baidu.com/genimage?%s" % self.vcode_str
        img_file = os.path.join(os.getcwd(), 'vcode.jpg')
        resp = self.sess.get(img_url, headers=self.headers)
        with open(img_file, "wb") as f:
            for item in resp:
                f.write(item)

        # 打开验证码图片
        os.system('start ' + img_file)
        self.vcode_input = str(raw_input(u'请输入验证码(回车更换): '))

    def sharedownload(self, link):  # 无验证码的情况
        api_url = 'http://pan.baidu.com/api/sharedownload'
        payload = {
            'sign': self.sign,
            'timestamp': self.timestamp,
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
        }
        self.extra = '{"sekey":"' + urllib.unquote(self.sess.cookies['BDCLND']) + '"}'
        data = {
            'encrypt': '0',
            'extra': self.extra,
            'product': 'share',
            'type': 'nolimit',
            'uk': self.uk,
            'primaryid': self.primaryid,
            'fid_list': self.fid_list,
        }
        resp = self.sess.post(api_url, data=data, params=payload, headers=self.headers)
        return json.loads(resp.text)

    def sharedownload_2(self, link):  # 有验证码的情况
        api_url = 'http://pan.baidu.com/api/sharedownload'
        payload = {
            'sign': self.sign,
            'timestamp': self.timestamp,
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
        }

        data = {
            'encrypt': '0',
            'extra': self.extra,
            'product': 'share',
            'vcode_input': self.vcode_input,
            'vcode_str': self.vcode_str,
            'type': 'nolimit',
            'uk': self.uk,
            'primaryid': self.primaryid,
            'fid_list': self.fid_list,
        }

        resp = self.sess.post(api_url, data=data, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        return js

    def get_download_link(self, link, pwd):
        try:
            self.get_baidu_cookie()  # 初始化cookie

            if not self.verify_pwd(link, pwd):  # 验证文件密码
                print u'文件密码错误！'
                return

            self.get_params(link)  # 密码验证成功后，获取网页的参数

            js = self.sharedownload(link)  # 第一次尝试获取下载链接，json解析后返回dict

            flag = True
            while flag:
                if js['errno'] == 0:  # 解析成功
                    print u'文件名：' + js['list'][0]['server_filename']
                    print u'下载链接：' + js["list"][0]['dlink']
                    print u'文件大小：' + str(js['list'][0]['size']/1000000.0) + 'MB'
                    flag = False
                elif js['errno'] == -20:
                    print u'开始下载验证码……'
                    self.get_vcode(link)
                    js = self.sharedownload_2(link)
                else:
                    print u'未知错误，错误代码如下:'
                    print js
                    return
        except Exception as e:
            print 'Exception:', e
            raise


if __name__ == '__main__':
    baidu = BaiduParser()
    link = 'https://pan.baidu.com/s/1xxxx'      # 私密分享文件的链接
    pwd = 'xxxxxx'                                  # 提取密码
    baidu.get_download_link(link, pwd)
