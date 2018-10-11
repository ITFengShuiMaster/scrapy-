# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlePipeline(object):
    def process_item(self, item, spider):
        return item


class JsonArticlePipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', mode='w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()


class JsonExportPipeline(object):
    def __init__(self):
        self.file = open("article_json_export.json", 'wb')
        self.export = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.export.start_exporting()

    def process_item(self, item, spider):
        self.export.export_item(item)
        return item

    def close_spider(self, spider):
        self.export.finish_exporting()
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        file_image_path = ''
        if "front_image_url" in item:
            for value in results:
                file_image_path = value[1]['path']
            item['front_image_path'] = file_image_path
        return item


class MySqlPipeline(object):
    #同步数据库操作
    def __init__(self):
        #self.conn = MySQLdb.connect('192.168.0.106', 'root', 'root', 'article_spider', charset="utf8", use_unicode=True)
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'wxhxx520', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = '''
            insert into article(title, url, url_object_id, point_nums, fav_nums)
            VALUES (%s, %s, %s, %s, %s)
        '''
        self.cursor.execute(insert_sql, (item['title'], item['url'], item['url_object_id'], item['point_nums'], item['fav_nums']))
        self.conn.commit()
        return item


class MySqlTwistedPipeline(object):
    #异步数据库操作
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        db_params = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **db_params)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql = '''
                    insert into article(title, url, url_object_id, point_nums, fav_nums)
                    VALUES (%s, %s, %s, %s, %s)
                '''
        params = (item['title'], item['url'], item['url_object_id'], item['point_nums'], item['fav_nums'])
        print(insert_sql, params)
        cursor.execute(insert_sql, params)
