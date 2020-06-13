# -*- coding: utf-8 -*-

import json
import os
import os.path
import tarfile
import sys
from elasticsearch import Elasticsearch
import glob
import redis
import requests
import scrapy
import markdown
from bs4 import BeautifulSoup
import re
from scrapy.selector import Selector
import codecs
import html2text
import hashlib
import tldextract

import configs
import config
from proj_utils.es import EsUtil
from multiprocessing import Pool  # 计算密集型
from multiprocessing.dummy import Pool as ThreadPool  # IO密集型

from proj_utils.data import remove_style
from proj_utils.data import remove_style_fully
from proj_utils.es import get_site_size
sys.path.append('./recursive_crawler/recursive_crawler/')
import filter.request as rqst

_INDEX = 'yls'  # 修改为索引名
_TYPE = 'yls01'  # 修改为类型名
HOST_TEMPLITE = "{host}:{port}"

_CFG = configs.Configs(config)
_ES = Elasticsearch(HOST_TEMPLITE.format(host=_CFG['ES_HOST'], port=_CFG['ES_PORT']))
_ES_Util = EsUtil(_ES, _INDEX, _TYPE)


def _id(source):
    if u'url' in source:
        r = scrapy.Request(source['url'])
        return rqst.request_fingerprint(r)
    elif u'code' in source:
        return source[u'code']
    else:
        md5 = hashlib.md5(source['title']+source['keywords']).hexdigest()
        source['url'] = 'http://med.wanfangdata.com.cn/'
        return md5


def extract_file(filename, origin=None):
    print(filename)
    rqsts = []
    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break
            try:
                json_obj = json.loads(line.strip())
            except:
                print>> sys.stderr, line
                continue
            if origin:
                json_obj['origin'] = origin
            rqsts.append(json_obj)
            if len(rqsts) >= 10:
                _ES_Util.minsert(rqsts, id=_id)
                rqsts = []
    _ES_Util.minsert(rqsts, id=_id)


def parse_file(jsonl_file_dir):
    filenames = list(glob.iglob(jsonl_file_dir + '/*.jsonl'))
    pool = ThreadPool(4)
    pool.map(extract_file, filenames)
    pool.close()
    pool.join()


def online_trans(src_text):
    src_text = remove_style_fully(src_text)
    res = []
    for text in src_text.split('\n'):
        payload = {
            'from': 'en',
            'to': 'zh',
            'src_text': text
        }
        r = requests.post(_CFG['NIU_HOST'], data=payload)
        tgt = r.json()[u'tgt_text']
        res.append(tgt)
    ans = u'\n'.join(res).encode('utf-8')
    return ans




def translate(json_obj):
    json_obj['content'] = online_trans(json_obj['content'])
    return json_obj


def extract_tgz(filename, origin):
    print(filename)
    rqsts = []
    tar_file = tarfile.open(filename, 'r')
    for name in tar_file.getnames():
        if name[-5:] != 'jsonl':
            print('not match', name)
            continue
        f = tar_file.extractfile(name)
        while True:
            line = f.readline()
            if not line:
                break
            try:
                json_obj = json.loads(line)
                json_obj = translate(json_obj)
            except Exception, e:
                print>> sys.stderr, e
                continue
            json_obj['origin'] = origin
            rqsts.append(json_obj)
            if len(rqsts) >= 4:
                _ES_Util.minsert(rqsts, id=_id)
                rqsts = []
    _ES_Util.minsert(rqsts, id=_id)


glb_origin = None


def _extract(name):
    return extract_tgz(name, glb_origin)


def parse_tgz(tgz_file_dir, origin='en'):
    global glb_origin
    glb_origin = origin
    pool = Pool(4)
    filenames = list(glob.iglob(tgz_file_dir + '/*.jsonl.tgz'))
    pool.map(_extract, filenames)
    pool.close()
    pool.join()


def parse_redis(origin='zh'):
    _ES_Plain = EsUtil(_ES, 'plain', _TYPE)
    rqsts = []
    plain_rqsts = []
    r = redis.StrictRedis(host=_CFG['REDIS_HOST'], port=_CFG['REDIS_PORT'], db=0)
    while True:
        _, data = r.blpop('jsonl')  # 阻塞等待，直到有数据
        try:
            json_obj = json.loads(data)
        except Exception, e:
            print>> sys.stderr, e
            continue
        json_obj['origin'] = origin
        plain_obj = json_obj.copy()
        plain_obj[u"content"] = remove_style(plain_obj[u"content"])
        url = plain_obj[u"url"]
        extracted = tldextract.extract(url)
        site = extracted.domain + '.' + extracted.suffix
        plain_obj[u"site_code"] = get_site_size(r, site)
        rqsts.append(json_obj)
        plain_rqsts.append(plain_obj)
        if len(rqsts) >= 10:
            _ES_Util.minsert(rqsts, id=_id)
            _ES_Plain.minsert(plain_rqsts, id=_id)
            rqsts = []
            plain_rqsts = []


def parse_html(html_file_dir, origin='zh'):
    rqsts = []
    for parent_dir, dir_name, filenames in os.walk(html_file_dir):
        for filename in filenames:
            if filename[-4:] != 'html' and filename[-3:] != 'htm':
                continue
            with codecs.open(os.path.join(parent_dir, filename), 'r', 'utf-8') as f:
                text = f.read()
                selector = Selector(text=text)
                title = selector.css('title::text').extract()
                print(title)
                if not title:
                    title = ''
                else:
                    title = title[0].encode("utf-8")
                description = selector.xpath(
                    "//meta[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')\
                    ,'description')]/@content").extract()
                if not description:
                    description = ''
                else:
                    description = description[0].encode('utf-8')
                keywords = selector.xpath(
                    "//meta[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')\
                    ,'keywords')]/@content").extract()
                if not keywords:
                    keywords = ''
                else:
                    keywords = keywords[0].encode('utf-8')
                converter = html2text.HTML2Text()
                converter.ignore_links = True
                content = converter.handle(text).encode('utf-8')
                data = {'title': title, 'keywords': keywords, 'description': description, 'content': content,
                        'origin': origin}
                rqsts.append(data)
                if len(rqsts) >= 10:
                    _ES_Util.minsert(rqsts, id=_id)
                    rqsts = []
    _ES_Util.minsert(rqsts, id=_id)


if __name__ == '__main__':
    # TODO: format with args
    if len(sys.argv) > 1:
        if sys.argv[1] == 'redis':
            print 'parse redis...'
            parse_redis()
        elif sys.argv[1] == 'file':
            file_path = sys.argv[2]
            parse_file(file_path)
        elif sys.argv[1] == 'tgz':
            tgz_path = sys.argv[2]
            parse_tgz(tgz_path)

    # _INDEX = 'ptn'  # 修改为索引名
    # _TYPE = 'ptn01'  # 修改为类型名
    # HOST_TEMPLITE = "{host}:{port}"
    #
    # _CFG = configs.Configs(config)
    # _ES = Elasticsearch(HOST_TEMPLITE.format(host=_CFG['ES_HOST'], port=_CFG['ES_PORT']))
    # _ES_Util = EsUtil(_ES, _INDEX, _TYPE)
    # extract_file('./ChineseBase/match.json')

    # tgz_file_dir = '/home/light/Documents/MedicalSE'
    # parse_tgz(tgz_file_dir)
    # parse_redis()
    # extract_tgz('/home/light/Documents/MedicalSE/8.jsonl.tgz', origin='en')
    # parse_html('/home/light/Documents/wanfang')
    # for filename in glob.iglob(tgz_file_dir + '/*.jsonl.tgz'):
    #     extract_tgz(filename, 'en')
