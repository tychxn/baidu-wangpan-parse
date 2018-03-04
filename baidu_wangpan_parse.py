#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Python解析百度云分享文件下载链接
    （只能解析单个分享文件下载地址，不能解析文件夹下载地址）
    基于Python2.7
'''

import requests

import re
import time
import json
import random
import os
import urllib
import argparse

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class BaiduWangpan(object):

    def __init__(self, isEncrypt, link, password):
        self.isEncrypt = isEncrypt
        self.link = link
        self.password = password

        self.sess = requests.Session()
        self.primaryId = ""
        self.uk = ""
        self.sign = ""
        self.timestamp = ""
        self.fidList = ""
        self.verifyCodeStr = ""
        self.verifyCodeInput = ""
        self.headers = {
            'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'Host': 'pan.baidu.com',
            'Origin': 'https://pan.baidu.com'
        }

    def getBaiduCookie(self):    # 初始化cookie
        self.sess.get(url='http://pan.baidu.com', headers=self.headers)

    def verifyPassword(self):  # post文件密码用于验证
        url = 'https://pan.baidu.com/share/verify'

        match = re.match(r'http[s]?://pan.baidu.com/s/1(.*)', self.link)
        if not match:
            print u'Link match error!'
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
            'pwd': self.password,
            'vcode': '',
            'vcode_str': '',
        }

        self.headers['Referer'] = self.link

        resp = self.sess.post(url=url, data=data, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        if js['errno'] == 0:
            return True
        else:
            return False

    def getParams(self):  # 重新载入页面来获取后面所需的参数
        resp = self.sess.get(self.link, headers=self.headers)
        resp.encoding = 'utf-8'

        # 读取页面中的参数
        m = re.search('\"sign\":\"(.+?)\"', resp.text)
        self.sign = m.group(1)
        m = re.search('\"timestamp\":(.+?),\"', resp.text)
        self.timestamp = m.group(1)
        m = re.search('\"shareid\":(.+?),\"', resp.text)
        self.primaryId = m.group(1)
        m = re.search('\"uk\":(.+?),\"', resp.text)
        self.uk = m.group(1)
        m = re.search('\"fs_id\":(.+?),\"', resp.text)
        self.fidList = '[' + m.group(1) + ']'

    def getVerifyCode(self):  # 获取验证码并要求输入
        print u'Start downloading the verification code...'

        url = "http://pan.baidu.com/api/getvcode"
        payload = {
            'prod': 'pan',
            't': random.random(),
            'bdstoken': 'null',
            'channel': 'chunlei',
            'clienttype': '0',
            'web': '1',
            'app_id': '250528',
        }

        resp = self.sess.get(url=url, params=payload, headers=self.headers)
        js = json.loads(resp.text)
        self.verifyCodeStr = js['vcode']

        # 保存验证码
        image_file = 'verification_code.jpg'
        resp = self.sess.get(
            "http://pan.baidu.com/genimage?%s" % self.verifyCodeStr,
            headers=self.headers
        )
        with open (image_file, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                f.write(chunk)

        # 打开验证码图片
        if os.name == "nt": 
            os.system('start ' + image_file)  # for Windows
        else:
            if os.uname()[0] == "Linux":
                os.system("eog " + image_file)  # for Linux
            else:
                os.system("open " + image_file)  # for Mac

        self.verifyCodeInput = str(raw_input(u'Please enter the verification code (return change):'))

    def downloadResp(self, needVerify=False):
        url = 'http://pan.baidu.com/api/sharedownload'
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
            'product': 'share',
            'type': 'nolimit',
            'uk': self.uk,
            'primaryid': self.primaryId,
            'fid_list': self.fidList,
        }

        if self.isEncrypt:
            data['extra'] = '{"sekey":"' + urllib.unquote(self.sess.cookies['BDCLND']) + '"}'

        if needVerify:  # 需要验证码
            data['vcode_input'] = self.verifyCodeInput
            data['vcode_str'] = self.verifyCodeStr

        resp = self.sess.post(url=url, params=payload, data=data, headers=self.headers)
        return json.loads(resp.text)

    def getDownloadURL(self):
        try:
            self.getBaiduCookie()  # 初始化cookie

            if self.isEncrypt:
                if not self.verifyPassword():  # 验证文件密码
                    print u'Sharing file password error!'
                    return

            self.getParams()  # 密码验证成功后，获取网页的参数

            js = self.downloadResp(needVerify=False)  # 第一次尝试获取下载链接
            while True:
                if js['errno'] == 0:  # 获取下载链接成功
                    print u'Filename：' + js['list'][0]['server_filename']
                    print u'Download link：' + js["list"][0]['dlink']
                    print u'Size：' + str(js['list'][0]['size']/1000000.0) + 'MB'
                    break
                elif js['errno'] == -20:  # 需要验证码
                    self.getVerifyCode()
                    js = self.downloadResp(needVerify=True)
                else:
                    print u'Unknown error, the error code is as follows:'
                    print js
                    return
        except Exception as e:
            print 'Exception:', e
            raise

def str2bool(v):
    if v.lower() in ('true', 'yes', 't', 'y'):
        return True
    elif v.lower() in ('false', 'no', 'f', 'n'):
        return False
    else:
        raise argparse.ArgumentTypeError('Unsupported value encountered.')

def main(options):
    baiduWangpan = BaiduWangpan(isEncrypt=options.encrypt, link=options.link, password=options.password)
    baiduWangpan.getDownloadURL()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Baidu wangpan private sharing file download link.')
    parser.add_argument('-e', '--encrypt',
                       help='Whether sharing file is encrypted，input should be either "true" or "false"', 
                       type=str2bool, const=True, nargs='?', required=True)
    parser.add_argument('-l', '--link',
                       help='Baidu wangpan sharing file link', required=True)
    parser.add_argument('-p', '--password',
                       help='Baidu wangpan sharing file password')
    options = parser.parse_args()

    main(options)
