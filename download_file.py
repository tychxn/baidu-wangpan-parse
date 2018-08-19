#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re


def download_file(link, save_path_without_filename):
    '''
    @param link 真实的文件下载地址
    @param save_path_without_filename 存储的文件夹路径
    '''
    response = requests.get(link)

    http_header_content_disposition = response.headers['content-disposition']
    filename = re.findall('filename=\"(.+)\"', http_header_content_disposition)

    with open(save_path_without_filename + "/" + filename[0], 'wb') as file:
        file.write(response.content)
