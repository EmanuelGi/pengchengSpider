# -*- coding: utf-8 -*-


from elasticsearch import Elasticsearch
import markdown
import redis
import tldextract
from bs4 import BeautifulSoup
from es import EsUtil
from es import get_site_size

import sys
import re
sys.path.append("../")
import configs
import config

HOST_TEMPLITE = "{host}:{port}"

_CFG = configs.Configs(config)
_ES = Elasticsearch(HOST_TEMPLITE.format(host=_CFG['ES_HOST'], port=_CFG['ES_PORT']))

_ES_From = EsUtil(
    _ES,
    'yls',
    'yls01'
)
_ES_To = EsUtil(
    _ES,
    'plain',
    'yls01'
)


def remove_style(src_text):
    plain = markdown.markdown(src_text)
    soup = BeautifulSoup(plain, 'lxml')
    plain = soup.get_text()
    return plain


def remove_style_fully(src_text):
    link = r'!?\[(.|\n)*?\]\((.|\n)*?\)'
    src_text = re.sub(link, '', src_text)
    soup = BeautifulSoup(src_text, 'lxml')
    plain = soup.get_text()
    plain = markdown.markdown(plain)
    soup = BeautifulSoup(plain, 'lxml')
    plain = soup.get_text()
    blank = r'\n+'
    plain = re.sub(blank, '\n', plain)
    return plain


def transfer_data():
    r = redis.StrictRedis(host=_CFG['REDIS_HOST'], port=_CFG['REDIS_PORT'], db=0)
    ids = []
    requests = []
    for result in _ES_From.scan(size=10, scroll='10m'):
        ids.append(result[u'_id'])
        source = result[u'_source']
        content = remove_style(source[u'content'])
        source[u'content'] = content
        url = source[u'url']
        extracted = tldextract.extract(url)
        site = extracted.domain + '.' + extracted.suffix
        size = get_site_size(r, site)
        source[u'site_code'] = size
        requests.append(source)
        _ES_To.minsert(requests, ids=ids)
        requests = []
        ids = []


def set_site_code():
    r = redis.StrictRedis(host=_CFG['REDIS_HOST'], port=_CFG['REDIS_PORT'], db=0)
    client = redis.Redis(connection_pool=redis.BlockingConnectionPool(max_connections=15, host=_CFG['REDIS_HOST'], port=_CFG['REDIS_PORT']))
    rqsts = []
    query = {
        "query": {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": "site_code"
                    }
                }
            }
        }
    }
    for result in _ES_To.scan(request=query, size=10):
        source = result[u'_source']
        id = result[u'_id']
        url = source[u'url']
        extracted = tldextract.extract(url)
        site = extracted.domain + '.' + extracted.suffix
        size = get_site_size(r, site)
        rqsts.append({
            '_id': id,
            'site_code': size
        })
        if len(rqsts) > 10:
            _ES_To.mupdate(rqsts)
            rqsts = []
    if len(rqsts) > 10:
        _ES_To.mupdate(rqsts)


if __name__ == '__main__':
    # set_site_code()
    transfer_data()
