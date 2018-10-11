# -*- coding:utf-8 _*-  
__author__ = 'luyue'
__date__ = '2018/5/1 21:49'

import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    print(get_md5('http:www.baidu.com'))