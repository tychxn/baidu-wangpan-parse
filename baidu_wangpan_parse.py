#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Python解析百度云分享文件下载链接
    基于Python2.7
'''

import os
import time
import re
import json
import random
import urllib
import argparse

import requests

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class BaiduWangpan(object):

    def __init__(self, isEncrypt, isFolder, link, password):
        self.isEncrypt = isEncrypt
        self.isFolder = isFolder
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
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'Host': 'pan.baidu.com',
            'Origin': 'https://pan.baidu.com',
        }

    def initCookie(self):  # init cookies
        self.sess.get(url='http://pan.baidu.com', headers=self.headers)

    def verifyPassword(self):  # verify file password
        match = re.match(r'http[s]?://pan.baidu.com/s/1(.*)', self.link)
        if not match:
            print u'Link match error!'
            return False

        url = 'https://pan.baidu.com/share/verify'
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
        return True if js['errno'] == 0 else False

    def getParams(self):  # reload the page to get the parameters needed later
        try:
            resp = self.sess.get(self.link, headers=self.headers)
            resp.encoding = 'utf-8'
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
            return True
        except Exception as e:
            return False

    def getVerifyCode(self):
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

        # save verify code
        image_file = 'verification_code.jpg'
        resp = self.sess.get(
            url="http://pan.baidu.com/genimage?%s" % self.verifyCodeStr,
            headers=self.headers
        )
        with open(image_file, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                f.write(chunk)

        # open verify code
        if os.name == "nt": 
            os.system('start ' + image_file)  # for Windows
        else:
            if os.uname()[0] == "Linux":
                os.system("eog " + image_file)  # for Linux
            else:
                os.system("open " + image_file)  # for Mac

        self.verifyCodeInput = str(raw_input(u'Please enter the verification code (return change):'))

    def getRespJson(self, needVerify=False):
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

        if self.isFolder:
            data['type'] = 'batch'

        if self.isEncrypt:
            data['extra'] = '{"sekey":"' + urllib.unquote(self.sess.cookies['BDCLND']) + '"}'

        if needVerify:
            data['vcode_input'] = self.verifyCodeInput
            data['vcode_str'] = self.verifyCodeStr

        resp = self.sess.post(url=url, params=payload, data=data, headers=self.headers)
        return json.loads(resp.text)

    def getDownloadLink(self):
        try:
            self.initCookie()
            if self.isEncrypt:
                if not self.verifyPassword():  # verify file password
                    print u'Sharing file password error!'
                    return None

            if not self.getParams():
                print u'It seems that the file needs password'
                return None

            # try to get the download link for the first time (without verify code)
            js = self.getRespJson(needVerify=False)
            while True:
                if js['errno'] == 0:  # success
                    return js['dlink'] if self.isFolder else js["list"][0]['dlink']
                elif js['errno'] == -20:  # need verify code
                    self.getVerifyCode()
                    js = self.getRespJson(needVerify=True)  # get the download link with verify code
                else:
                    print u'Unknown error, the error code is as follows:'
                    print js
                    return None
        except Exception:
            print 'Exception:', e
            raise


def main(options):
    wangpan = BaiduWangpan(isEncrypt=True if options.password else False,
                           isFolder=options.folder,
                           link=options.link,
                           password=options.password)
    link = wangpan.getDownloadLink()
    print link

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Baidu wangpan sharing file download link.')
    parser.add_argument('link', help='Baidu wangpan sharing file link')
    parser.add_argument('password', nargs='?', help='Baidu wangpan sharing file password')
    parser.add_argument('-f', '--folder', help='if sharing file is a folder', action="store_true")
    options = parser.parse_args()

    main(options)
