# -*- coding:utf-8 _*-  
__author__ = 'luyue'
__date__ = '2018/4/30 16:42'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "jpbbole"])
execute(["scrapy", "crawl", "basketball"])