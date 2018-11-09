# -*- coding: utf-8 -*-
import re
import sys
import time

import requests
from uuid import uuid4

from util import *

if (sys.version_info < (3, 0)):
    input = raw_input


class BaiduLogin(object):
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
            'referer': 'https://pan.baidu.com/',
        }
        self.sess = requests.session()
        self.gid = str(uuid4()).upper()
        self.token = ''
        self.key = ''

    def _init_cookies(self):
        """初始化cookies
        :return:
        """
        self.sess.get(url='https://pan.baidu.com/', headers=self.headers)

    def _get_token(self):
        """获取登陆token
        :return:
        """
        url = 'https://passport.baidu.com/v2/api/?getapi'
        payload = {
            'getapi': '',
            'tpl': 'mn',
            'apiver': 'v3',
            'tt': str(int(time.time() * 1000)),
            'class': 'login',
            'gid': self.gid,
            'loginversion': 'v4',
            'logintype': 'dialogLogin',
            'traceid': '',
            'callback': 'bd__cbs__pivyke',
        }
        resp = self.sess.get(url, params=payload, headers=self.headers)
        js = parse_json(resp.text.replace("\'", "\""))
        self.token = js['data']['token']

    def _get_public_key(self):
        """获取RSA公钥
        :return: RSA公钥
        """
        url = 'https://passport.baidu.com/v2/getpublickey'
        payload = {
            'token': self.token,
            'tpl': 'mn',
            'apiver': 'v3',
            'tt': str(int(time.time() * 1000)),
            'gid': self.gid,
            'loginversion': 'v4',
            'traceid': '',
            'callback': 'bd__cbs__h02h0j'
        }
        resp = self.sess.get(url, params=payload, headers=self.headers)
        js = parse_json(resp.text.replace("\'", "\""))
        self.key = js.get('key')
        return js.get('pubkey')

    def _load_local_cookies(self):
        """加载并验证本地cookies
        :return: True/False cookies是否有效
        """
        try:
            self.sess.cookies.update(load_cookies())
            resp = self.sess.get(url='https://passport.baidu.com/center', allow_redirects=False)
            return True if resp.status_code == requests.codes.OK else False
        except Exception as e:
            return False

    def login_by_username(self, username, password):
        """用户名密码登陆
        :param username: 用户名
        :param password: 密码
        :return:
        """
        if self._load_local_cookies():
            return

        self._init_cookies()
        self._get_token()

        url = 'https://passport.baidu.com/v2/api/?login'
        data = {
            'staticpage': 'https://www.baidu.com/cache/user/html/v3Jump.html',
            'charset': 'UTF-8',
            'token': self.token,
            'tpl': 'netdisk',
            'subpro': 'netdisk_web',
            'apiver': 'v3',
            'tt': str(int(time.time() * 1000)),
            'codestring': '',
            'safeflg': '0',
            'u': 'https://www.baidu.com/',
            'isPhone': 'false',
            'detect': '1',
            'gid': self.gid,
            'quick_user': '0',
            'logintype': 'dialogLogin',
            'logLoginType': 'pc_loginDialog',
            'idc': '',
            'loginmerge': 'true',
            'splogin': 'rate',
            'username': username,
            'password': encrypt_pwd(password, self._get_public_key()),
            'rsakey': self.key,
            'crypttype': '12',
            'ppui_logintime': 254896,
            'countrycode': '',
            'fp_uid': '08cc104e76b697a29930f9afdcdbdf8a0',
            'fp_info': '08cc104e76b697a29930f9afdcdbdf8a002~~~j-jjnTfCHkdUvit_~jjavfBv5ci8WJ-8rC_ffBv5ci8WJ-viQ_ajhJuXjhJuFjjuKjhL2Rf0SjQqlV8KRlXrtSv5nRv5CSv2d4Qq7iXyviX5mT8imRv5nRMy-i85a6X5miv2yRMdv782yl8rnkviyRMdQI8rCT85nTX5d4QklV3z0LQkc_w~jusfCvryUvm__I~jmU~jmz~juQf0t~ck~FakeTaK3dGz7~QkJIXp-lQrmLcqjINq0xAqHnAk8SAEHUNn3FQzS~NZ70Az0xAqHiHkdy3K3BAzHLOE8dAW8dQk3FQWuLaKdxaE8fAk3tHnSvaKHyOEwFNzdy3EjrAkR63ER69x~k3KsiOEjUXrnU8Z--9rnlvryB908DAk8fNk0k3c3LaK8DvryUvbtlJf0Tx3qHzaKHLNbRrAkSeNERBak06OEjUQTRrvz8yvqsd8idr8q0xX5drv5JSaicRX2nSv2CT8kn-vrakvzGr85miXqHx85Q785mR8E3rar~xaEcRaimk3q3~MzGd3z0SAbG4akjeAKHUOE8~NqdFAW84Xqa-3rudXEsd323zvzal85cTaEciaE3yar3r35ur3ztTvrdx3zHzXqt7v5cRvzsx85aTa5yivka7vqsd8rCI3J__y~juO~jux~juB~juYjjtrfC1zJeC6-_CfBNERfAzjTAJ__j~juMjjmZ~jmE~jmg~jmG~jmH~jmlfa95nU82t782C-X2tiX2Q68it68C__',
            'loginversion': 'v4',
            'dv': 'tk0.43083294066104651525942832352@oop0d-sGFb6mgFCFYuF3psLelCFehN6rhNLihP8isi7io34k5gsk5KNkT~4kqbJ0pDBeohrJlNFpsCL~0jLeljALs~QKl-Hmj-6rFK6LjKDmjj4pBhr3QECFeNLehrFpfg6plN82p~8iQa8UCb6G0is~Qfs~qb6mgFCFYuF3psLelCFehN6rhNLihP8isi7io34k5-6kqeNk0j61jj4pBhr3QECFeNLehrFpfg6plN82p~8iQa8UCb6G6-6ksfrp0Wr6r3-4kFjDmjwsr0~4ujw6r5bsr6y4k3~6~0bNk0-61j~6~qb6rT~6rCbJ0pDBeohrJlNFpsCL~0jLeljALs~QKl-Hujg6k5b6~8-4k0YsG0w4pBhr3QECFeNLehrFpfg6plNHUl-7Lj~s~Tb6~AK4k5ws~3Y4pBhr3QECFeNLehrFpfg6plNHUl-7Lj_-~~Mz~CjRqlMhCph6Ej-4kA~wplQ2bj4GC~6kT~6G3w6kAK6rqwsGFgsr5eDrC-Dk6-6~F-hplMuBw8u6V4-liQi8IAUpcHuFIAKld4-ge7UBXHUXIH9C_ypt6mjj4k0-6r5bs~CK4k0e6~AbDkAw4k0e6~Ab6rF~s1jy6~8_',
            'traceid': '',
            'callback': 'parent.bd__pcbs__oxzeyj'
        }

        for _ in range(8):
            resp = self.sess.post(url=url, headers=self.headers, data=data)

            m = re.search('.*href \+= "(.*)"\+accounts', resp.text)
            _url = m.group(1)
            d = dict([x.split("=") for x in _url.split("&")])

            err_no = d.get('err_no')
            if err_no == '0':
                print('Login success！')
                save_cookies(self.sess)
                return True
            elif err_no == '6' or err_no == '257':
                code_string = d.get('codeString')
                data['codestring'] = code_string
                resp = self.sess.get(
                    url='https://passport.baidu.com/cgi-bin/genimage?{}'.format(code_string),
                    headers=self.headers
                )
                image_path = os.path.join(os.getcwd(), 'vcode-login.jpg')
                save_image(resp, image_path)
                open_image(image_path)
                verify_code = input('Please enter the verify code for login(return change):')
                data['verifycode'] = verify_code
            else:
                print('Err_no：', err_no)
                exit()
        raise LoginError('Login Fail！')


class LoginError(Exception):
    pass
