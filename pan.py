#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Python解析百度云分享文件下载链接
    兼容Python2/3
'''
from __future__ import print_function
import re
import sys
import time
import json
import random

import requests

from util import load_cookies, save_image, open_image

if (sys.version_info > (3, 0)):
    import urllib.parse as parse
else:
    import urllib as parse
    input = raw_input


class BaiduPan(object):

    def __init__(self, is_encrypt, is_folder, link, password):
        self.is_encrypt = is_encrypt
        self.is_folder = is_folder
        self.link = link
        self.password = password

        self.sess = requests.session()
        self.sess.cookies.update(load_cookies())

        self.primary_id = ''
        self.uk = ''
        self.sign = ''
        self.timestamp = ''
        self.fid_list = ''
        self.verify_code_str = ''
        self.verify_code_input = ''
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'Origin': 'https://pan.baidu.com',
        }

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

    def get_params(self):  # get the parameters needed later
        self.sess.get(url='http://pan.baidu.com', headers=self.headers)

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
        except Exception as e:
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

        resp = self.sess.get(
            url='http://pan.baidu.com/genimage?%s' % self.verify_code_str,
            headers=self.headers
        )

        # save verify code
        image_file = 'vcode-getlink.jpg'
        save_image(resp, image_file)
        open_image(image_file)
        self.verify_code_input = input('Please enter the verify code for get link(return change):')

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
            headers=self.headers
        )
        return json.loads(resp.text)

    def get_download_link(self):
        try:
            if self.is_encrypt:
                if not self.verify_password():  # verify file password
                    raise GetLinkError('Sharing file password error!')

            if not self.get_params():
                raise GetLinkError('It seems that the file needs password.')

            # try to get the download link for the first time (without verify code)
            js = self.get_resp_json(need_verify=False)
            while True:
                err_no = js.get('errno')
                if err_no == 0:  # success
                    return js['dlink'] if self.is_folder else js['list'][0]['dlink']
                elif err_no == -20:  # need verify code
                    self.get_verify_code()
                    # get the download link with verify code
                    js = self.get_resp_json(need_verify=True)
                else:
                    print('Unknown error, the error message is as follows:')
                    raise GetLinkError(js)
        except Exception as e:
            print('Exception:', e)
            raise


class GetLinkError(Exception):
    pass
