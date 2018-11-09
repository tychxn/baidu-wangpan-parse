# -*- coding: utf-8 -*-
import argparse

from pan import BaiduPan
from login import BaiduLogin
from config import global_config


def main(options):
    login = BaiduLogin()
    login.login_by_username(
        username=global_config.get('account', 'username'),
        password=global_config.get('account', 'password')
    )
    pan = BaiduPan(
        is_encrypt=True if options.password else False,
        is_folder=options.folder,
        link=options.link,
        password=options.password
    )
    link = pan.get_download_link()
    print(link)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Baidu wangpan sharing file download link.')
    parser.add_argument('link', help='Baidu wangpan sharing file link')
    parser.add_argument('password', nargs='?', help='Baidu wangpan sharing file password')
    parser.add_argument('-f', '--folder', help='if sharing file is a folder', action='store_true')
    options = parser.parse_args()
    main(options)
