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

        self.shareid = ""
        self.uk = ""
        self.sign = ""
        self.timestamp = ""
        self.fid_list = ""
        self.vcode_str = ""
        self.vcode_input = ""
        self.extra = ""

        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
        }

    def get_baidu_cookie(self):    # 初始化cookie
        url = 'http://pan.baidu.com'
        self.sess.get(url, headers = self.headers)

    def get_real_url(self, link):  # 获取文件真正的访问链接
        try:
            resp = self.sess.get(link, headers = self.headers)

            m = re.search('.+?shareid=(\d+)&uk=(\d+)', resp.url)
            self.shareid = m.group(1)
            self.uk = m.group(2)

            # 构成文件的真正访问地址
            real_url = "http://pan.baidu.com/share/link?shareid=%s&uk=%s" % (self.shareid, self.uk)
        except Exception as e:
            print 'Exception:', e
            raise

        return real_url

    def verify_pwd(self, real_url, pwd):  # post文件密码用于验证
        verify_url = 'http://pan.baidu.com/share/verify'
        payload = {
            'shareid': self.shareid,
            'uk': self.uk,
            't': '%d' % (time.time() * 1000),
            'bdstoken': 'null',
            'channel': 'channel',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
            'logid': '',
        }

        data = {
            'pwd': pwd,
            'vcode': '',
            'vcode_str': '',
        }

        self.headers['Referer'] = real_url;

        resp = self.sess.post(verify_url, data=data, params=payload, headers=self.headers)

        js = json.loads(resp.text)
        if js['errno'] != 0:    # 文件密码错误
            return False
        else:                   # 密码正确
            return True


    def get_params(self, real_url):  # 重新载入页面来获取后面所需的参数
        resp = self.sess.get(real_url, headers=self.headers)
        resp.encoding = 'utf-8'

        # 读取页面中的参数
        m = re.search('\"sign\":\"(.+?)\"', resp.text)
        self.sign = m.group(1)
        m = re.search('\"timestamp\":(.+?),\"', resp.text)
        self.timestamp = m.group(1)
        m = re.search('\"fs_id\":(.+?),\"', resp.text)
        self.fid_list = '[' + m.group(1) + ']'


    def get_vcode(self, real_url):  # 获取验证码并要求输入
        vcode_str_url = "http://pan.baidu.com/api/getvcode"

        payload = {
            'prod': 'pan',
            't': random.random(),
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
            'logid': '',
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
        self.vcode_input = str(raw_input(u'请输入验证码(回车更换): '.encode('gbk')))

    def sharedownload(self, real_url):  # 无验证码的情况
        api_url = 'http://pan.baidu.com/api/sharedownload'
        payload = {
            'sign': self.sign,
            'timestamp': self.timestamp,
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
            'logid': '',
        }

        self.extra = '{"sekey":"' + urllib.unquote(self.sess.cookies['BDCLND']) + '"}'

        data = {
            'encrypt': '0',
            'extra': self.extra,
            'product': 'share',
            'uk': self.uk,
            'primaryid': self.shareid,
            'fid_list': self.fid_list,
        }

        resp = self.sess.post(api_url, data=data, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        return js

    def sharedownload_2(self, real_url):  # 有验证码的情况（可以和无验证码情况合并）
        api_url = 'http://pan.baidu.com/api/sharedownload'
        payload = {
            'sign': self.sign,
            'timestamp': self.timestamp,
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
            'logid': '',
        }

        data = {
            'encrypt': '0',
            'extra': self.extra,
            'product': 'share',
            'uk': self.uk,
            'primaryid': self.shareid,
            'fid_list': self.fid_list,
            'vcode_input': self.vcode_input,
            'vcode_str': self.vcode_str,
        }

        resp = self.sess.post(api_url, data=data, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        return js

    def get_download_link(self, link, pwd):
        try:
            self.get_baidu_cookie()  # 初始化cookie

            real_url = self.get_real_url(link)   # 访问加密分享链接，以获取真正的地址

            if not self.verify_pwd(real_url, pwd):  # 验证文件密码
                print u'文件密码错误！'
                return

            self.get_params(real_url)  # 密码验证成功后，获取网页的参数

            js = self.sharedownload(real_url)  # 第一次尝试获取下载链接，json解析后返回dict

            flag = True
            while flag:
                if (js['errno'] == 0):  # 解析成功
                    print u'文件名：' + js['list'][0]['server_filename']
                    print u'下载链接：' + js["list"][0]['dlink']
                    print u'文件大小：' + str(js['list'][0]['size']/1000000.0) + 'MB'
                    flag = False
                elif (js['errno'] == -20):
                    print u'开始下载验证码……'
                    self.get_vcode(real_url)
                    js = self.sharedownload_2(real_url)
                else:
                    print u'未知错误，错误代码如下:'
                    print js
                    return
        except Exception as e:
            print 'Exception:', e
            raise

if __name__ == '__main__':
    baidu = BaiduParser()
    link = 'http://pan.baidu.com/s/xxxxxxxx'      # 私密分享文件的链接
    pwd = 'xxxx'                                  # 提取密码
    baidu.get_download_link(link, pwd)