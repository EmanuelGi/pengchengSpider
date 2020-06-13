# -*- coding: utf-8 -*-

import datetime
import MySQLdb
import redis
import sys
sys.path.append('../')
import configs
import config

cfg = configs.Configs(config)
if cfg['MYSQL_PORT']:
    db = MySQLdb.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], \
                              passwd=cfg['MYSQL_PASSWORD'], db=cfg['MYSQL_DB'], port=cfg['MYSQL_PORT'])
else:
    db = MySQLdb.connect(host=cfg['MYSQL_HOST'], user=cfg['MYSQL_USER'], \
                              passwd=cfg['MYSQL_PASSWORD'], db=cfg['MYSQL_DB'])
cursor = db.cursor()

now = datetime.datetime.now()
before = now + datetime.timedelta(days=-30)

r = redis.StrictRedis(host=cfg['REDIS_HOST'], port=cfg['REDIS_PORT'], db=0)
pipe = r.pipeline()

select_fingerprint = "SELECT fingerprint FROM visited where last_time < '{before}'".format(before=before)
cursor.execute(select_fingerprint)

while True:
    fp = cursor.fetchone()
    if not fp:
        break
    pipe.srem('RecursiveSpider:dupefilter', fp[0])
pipe.execute()

