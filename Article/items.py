# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import re

import scrapy

from scrapy.loader.processors import MapCompose, TakeFirst, Join
from scrapy.loader import ItemLoader
from datetime import datetime


class ArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoder(ItemLoader):
    default_output_processor = TakeFirst()


def create_date2date(value):
    date = value.strip().replace('·', '').strip()
    try:
        create_date = datetime.strptime(date, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.now().date()
    return create_date


def get_nums(value):
    match_parten = '.*?(\d+).*'
    match_obj = re.match(match_parten, value)
    if match_obj:
        nums = match_obj.group(1)
    else:
        nums = 0
    return nums


def get_value(value):
    return value


def get_tags(value):
    if "评论" in value:
        return ""
    return value


class JobBoleArticleItem(scrapy.Item):
    url = scrapy.Field()
    url_object_id = scrapy.Field()#md5压缩
    title = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor = MapCompose(get_value)
    )
    front_image_path = scrapy.Field()#保存的本地路径
    create_date = scrapy.Field(
        input_processor=MapCompose(create_date2date)
    )
    point_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(get_tags),
        output_processor=Join(',')  # Join可以连接列表中的值
    )

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole_article(title, url, create_date, fav_nums, front_image_url, front_image_path,
            point_nums, fav_nums, tags, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE content=VALUES(fav_nums)
        """

        fron_image_url = ""
        # content = remove_tags(self["content"])

        if self["front_image_url"]:
            fron_image_url = self["front_image_url"][0]
        params = (self["title"], self["url"], self["create_date"], self["fav_nums"],
                  fron_image_url, self["front_image_path"], self["praise_nums"], self["comment_nums"],
                  self["tags"], self["content"])
        return insert_sql, params
