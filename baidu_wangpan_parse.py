#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Python解析百度云分享文件下载链接
    兼容Python2/3
'''
from __future__ import print_function
import os
import sys
import time
import re
import json
import random
import argparse

import requests

if (sys.version_info > (3, 0)):
    import urllib.parse as parse
else:
    import urllib as parse
    input = raw_input


class BaiduWangpan(object):

    def __init__(self, is_encrypt, is_folder, link, password):
        self.is_encrypt = is_encrypt
        self.is_folder = is_folder
        self.link = link
        self.password = password

        self.sess = requests.Session()
        self.primary_id = ''
        self.uk = ''
        self.sign = ''
        self.timestamp = ''
        self.fid_list = ''
        self.verify_code_str = ''
        self.verify_code_input = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'Host': 'pan.baidu.com',
            'Origin': 'https://pan.baidu.com',
        }

    def init_cookie(self):  # init cookies
        self.sess.get(url='http://pan.baidu.com', headers=self.headers)

    def verify_password(self):  # verify file password
        match = re.match(r'http[s]?://pan.baidu.com/s/1(.*)', self.link)
        if not match:
            print('Link match error!')
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
        resp = self.sess.post(
            url=url,
            data=data,
            params=payload,
            headers=self.headers)
        js = json.loads(resp.text)
        return True if js['errno'] == 0 else False

    def get_params(self):  # reload the page to get the parameters needed later
        try:
            resp = self.sess.get(self.link, headers=self.headers)
            resp.encoding = 'utf-8'
            m = re.search('\"sign\":\"(.+?)\"', resp.text)
            self.sign = m.group(1)
            m = re.search('\"timestamp\":(.+?),\"', resp.text)
            self.timestamp = m.group(1)
            m = re.search('\"shareid\":(.+?),\"', resp.text)
            self.primary_id = m.group(1)
            m = re.search('\"uk\":(.+?),\"', resp.text)
            self.uk = m.group(1)
            m = re.search('\"fs_id\":(.+?),\"', resp.text)
            self.fid_list = '[' + m.group(1) + ']'
            return True
        except Exception:
            return False

    def get_verify_code(self):
        print('Start downloading the verification code...')
        url = 'http://pan.baidu.com/api/getvcode'
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
        self.verify_code_str = js['vcode']

        # save verify code
        image_file = 'verification_code.jpg'
        resp = self.sess.get(
            url='http://pan.baidu.com/genimage?%s' % self.verify_code_str,
            headers=self.headers
        )
        with open(image_file, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                f.write(chunk)

        # open verify code
        if os.name == 'nt':
            os.system('start ' + image_file)  # for Windows
        else:
            if os.uname()[0] == 'Linux':
                os.system('eog ' + image_file)  # for Linux
            else:
                os.system('open ' + image_file)  # for Mac

        self.verify_code_input = input('Please enter the verification code (return change):')

    def get_resp_json(self, need_verify=False):
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
            'primaryid': self.primary_id,
            'fid_list': self.fid_list,
        }

        if self.is_folder:
            data['type'] = 'batch'

        if self.is_encrypt:
            data['extra'] = '{"sekey":"' + parse.unquote(self.sess.cookies['BDCLND']) + '"}'

        if need_verify:
            data['vcode_input'] = self.verify_code_input
            data['vcode_str'] = self.verify_code_str

        resp = self.sess.post(
            url=url,
            params=payload,
            data=data,
            headers=self.headers)
        return json.loads(resp.text)

    def get_download_link(self):
        try:
            self.init_cookie()
            if self.is_encrypt:
                if not self.verify_password():  # verify file password
                    print('Sharing file password error!')
                    return None

            if not self.get_params():
                print('It seems that the file needs password.')
                return None

            # try to get the download link for the first time (without verify code)
            js = self.get_resp_json(need_verify=False)
            while True:
                if js['errno'] == 0:  # success
                    return js['dlink'] if self.is_folder else js['list'][0]['dlink']
                elif js['errno'] == -20:  # need verify code
                    self.get_verify_code()
                    # get the download link with verify code
                    js = self.get_resp_json(need_verify=True)
                else:
                    print('Unknown error, the error code is as follows:')
                    print(js)
                    return None
        except Exception as e:
            print('Exception:', e)
            raise


def main(options):
    wangpan = BaiduWangpan(is_encrypt=True if options.password else False,
                           is_folder=options.folder,
                           link=options.link,
                           password=options.password)
    link = wangpan.get_download_link()
    print(link)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Baidu wangpan sharing file download link.')
    parser.add_argument('link', help='Baidu wangpan sharing file link')
    parser.add_argument('password', nargs='?', help='Baidu wangpan sharing file password')
    parser.add_argument('-f', '--folder', help='if sharing file is a folder', action='store_true')
    options = parser.parse_args()
    main(options)
