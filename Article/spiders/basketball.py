# -*- coding: utf-8 -*-
import scrapy
import json
import numpy as np
import pandas as pd
#导入图表库以进行图表绘制
import matplotlib.pyplot as plt

class BasketballSpider(scrapy.Spider):
    name = 'basketball'
    allowed_domains = ['http://www.liyiok.cn/']
    start_urls = ['http://www.liyiok.cn/zstk5/zsjstk30179261037.html']

    def parse(self, response):
        agri_answer = ''.join(response.css("#content p::text").extract())
        agri_title = ''
        agri_result = ''

        # for index, data in enumerate(agri_answer):
        #     if index == 0:
        #         continue
        #     agri_title = data

