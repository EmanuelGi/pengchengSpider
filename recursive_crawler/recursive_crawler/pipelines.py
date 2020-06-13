# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb
import scrapy
import redis
import json
import sys
sys.path.append('../../../')
import configs
import config
from filter.request import request_fingerprint

class RecursiveCrawlerPipeline(object):

    def open_spider(self, spider):
        cfg = configs.Configs(config)
        if cfg['MYSQL_PORT']:
            self.db = MySQLdb.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], \
                                      passwd=cfg['MYSQL_PASSWORD'], db=cfg['MYSQL_DB'], port=cfg['MYSQL_PORT'])
        else:
            self.db = MySQLdb.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], \
                                      passwd=cfg['MYSQL_PASSWORD'], db=cfg['MYSQL_DB'])

        self.server = redis.StrictRedis(cfg['REDIS_HOST'], port=cfg['REDIS_PORT'], db=0)
        self.file = open(name='spider', mode='a')

    def process_item(self, item, spider):
        cursor = self.db.cursor()

        request = scrapy.Request(item['url'])
        fingerprint = request_fingerprint(request)

        upsert = """
        INSERT INTO visited(fingerprint) VALUES ('{fp}') ON DUPLICATE KEY 
        UPDATE last_time = NULL
        """.format(fp=fingerprint)


        try:
            cursor.execute(upsert)
            # 爬取的数据不推入redis中，直接保存到本地文件
            to_push = json.dumps(dict(item))
            # self.server.rpush('jsonl', to_push)
            self.file.write(to_push)
            self.file.write(',\n')
        except Exception, e:
            print e.message
            self.db.rollback()
        else:
            self.db.commit()
        cursor.close()
        return item

    def close_spider(self, spider):
        self.db.close()
        self.file.close()
