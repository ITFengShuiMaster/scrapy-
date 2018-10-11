# -*- coding: utf-8 -*-
import scrapy
import re
import datetime

from scrapy.http import Request
from scrapy.loader import ItemLoader
from urllib import parse
from Article.items import JobBoleArticleItem, ArticleItemLoder
from Article.utils.common import get_md5


class JpbboleSpider(scrapy.Spider):
    name = 'jpbbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
            1、获取所有文章的url并进行解析
            2、获取下一页url并交给scrapy进行下载
        :param response:
        :return:
        '''

        #提取文章url并交给scrapy进行下载
        article_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for article_node in article_nodes:
            article_url = article_node.css("::attr(href)").extract_first("")#文章url
            image_url = article_node.css("img::attr(src)").extract_first("")#文章封面图url
            url = parse.urljoin(response.url, article_url)
            image_url = parse.urljoin(response.url, image_url)
            yield Request(url=url, meta={"front_image_url":image_url}, callback=self.parse_details)

        #提取下一页并进行下载
        # next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        # if next_url:
        #     yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_details(self, response):
        article = JobBoleArticleItem()
        #获取文章封面图
        front_image_url = response.meta.get('front_image_url', "")

        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first('')
        create_date = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].\
            strip().replace('·', '').strip()
        point_nums = int(response.xpath('//span[@class=" btn-bluet-bigger href-style vote-post-up   register-user-only "]/h10/text()').extract_first("0"))

        fav_nums = response.xpath('//span[@class=" btn-bluet-bigger href-style bookmark-btn  register-user-only "]/text()').extract_first("0")
        match_regex = '.*?(\d+).*'
        match_obj = re.match(match_regex, fav_nums)
        if match_obj:
            fav_nums = int(match_obj.group(1))
        else:
            fav_nums = 0

        content = response.xpath('//div[@class="entry"]').extract_first(" ")
        tag = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tags = ','.join([ele for ele in tag if not ele.endswith('评论')])

        article['title'] = title
        article['url'] = response.url
        article['url_object_id'] = get_md5(response.url)
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article['create_date'] = create_date
        article['front_image_url'] = [front_image_url]
        article['point_nums'] = point_nums
        article['fav_nums'] = fav_nums
        article['content'] = content
        article['tags'] = tags

        #ItemLoder 方式提取item
        item_loder = ArticleItemLoder(item=JobBoleArticleItem(), response=response)
        item_loder.add_css("title", ".entry-header h1::text")
        item_loder.add_value("url", response.url)
        item_loder.add_value("url_object_id", get_md5(response.url))
        item_loder.add_value("front_image_url", [front_image_url,])
        item_loder.add_css("create_date", ".entry-meta-hide-on-mobile::text")
        item_loder.add_css("point_nums", ".btn-bluet-bigger.href-style.vote-post-up.register-user-only h10::text")
        item_loder.add_css("fav_nums", ".btn-bluet-bigger.href-style.bookmark-btn.register-user-only::text")
        item_loder.add_css("content", ".entry")
        item_loder.add_css("tags", ".entry-meta-hide-on-mobile a::text")

        article = item_loder.load_item()

        yield article
