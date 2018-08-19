#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import re
from tqdm import tqdm
import math


class DownloadFileTask(object):

    def __init__(self, link, save_path_without_filename="."):
        '''
        @param link 真实的文件下载地址
        @param save_path_without_filename 存储的文件夹路径
        '''
        self.link = link
        self.save_path_without_filename = save_path_without_filename

    def download_file(self):
        response = requests.get(self.link, stream=True)

        filename = "file.mobi"

        if 'content-disposition' in response.headers:

            http_header_content_disposition = response.headers['content-disposition']
            filename = re.findall('filename=\"(.+)\"',
                                  http_header_content_disposition)[0]

        total_size = int(response.headers['content-length'])
        chunk_size = 1024

        with open(self.save_path_without_filename + "/" + filename, 'wb') as file:
            for chunk in tqdm(response.iter_content(chunk_size), total=math.ceil(total_size // chunk_size), unit='KB', unit_scale=True):
                file.write(chunk)
