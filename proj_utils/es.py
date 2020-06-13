import elasticsearch.helpers
import sys
import time
from elasticsearch.exceptions import ConnectionTimeout


def get_site_size(r, site):
    size = r.hget(name='site', key=site)
    if not size:
        size = r.incr('size')
        r.hsetnx(key=site, name='site', value=size)
    return size

class EsUtil(object):
    def __init__(self, es, index, doc_type):
        self._es = es
        self._index = index
        self._doc_type = doc_type


    def mupdate(self, requests, **kwds):
        if not requests:
            return
        operation = {
            '_op_type': 'update',
            '_index': self._index,
            '_type': self._doc_type,
        }
        operation.update(kwds)
        new_rqsts = []
        for request in requests:
            value = operation.copy()
            value['_id'] = request.pop('_id')
            value['doc'] = request
            new_rqsts.append(value)
        while True:
            try:
                elasticsearch.helpers.bulk(self._es, new_rqsts)
                return
            except Exception, e:
                print>>sys.stderr, e.message
                time.sleep(2)
                continue


    def minsert(self, requests, **kwds):
        if not requests:
            return
        operation = {
            '_op_type': 'index',
            '_index': self._index,
            '_type': self._doc_type,
        }
        new_rqsts = []
        if 'id' in kwds:
            id_func = kwds.pop('id')
            operation.update(kwds)
            for request in requests:
                value = operation.copy()
                value['_source'] = request
                value['_id'] = id_func(request)
                new_rqsts.append(value)
        elif 'ids' in kwds:
            ids = kwds.pop('ids')
            operation.update(kwds)
            for request, idx in zip(requests, ids):
                value = operation.copy()
                value['_source'] = request
                value['_id'] = idx
                new_rqsts.append(value)
        while True:
            try:
                elasticsearch.helpers.bulk(self._es, new_rqsts)
                return
            except Exception, e:
                print>>sys.stderr, e
                time.sleep(2)
                continue


    def msearch(self, requests, **kwds):
        if not requests:
            return
        head = {
            "index": self._index,
            "type": self._doc_type
        }
        head.update(kwds)
        new_rqsts = []
        for body in requests:
            new_rqsts.append(head)
            new_rqsts.append(body)
        while True:
            try:
                res = self._es.msearch(body=new_rqsts)
                break
            except Exception, e:
                print>> sys.stderr, "Exception:", e
                time.sleep(1)
                continue
        res = res[u'responses']
        return res


    def search(self, request, **kwargs):
        args = {
            'index': self._index,
            'doc_type': self._doc_type,
            'body': request
        }
        args.update(kwargs)
        while True:
            try:
                return self._es.search(**args)
            except ConnectionTimeout, e:
                print>>sys.stderr, e
                time.sleep(2)
                continue

    def insert(self, request):
        # TODO
        pass

    def update(self, request, id, **kwargs):
        args = {
            'index': self._index,
            'doc_type': self._doc_type,
            'id': id,
            'body': {
                'doc': request
            }
        }
        args.update(kwargs)
        while True:
            try:
                return self._es.update(**args)
            except ConnectionTimeout, e:
                print>>sys.stderr, e
                time.sleep(2)
                continue

    def count_total(self):
        return self.count()

    def count(self, request=None):
        kwargs = {
            'index': self._index,
            'doc_type': self._doc_type
        }
        if request:
            kwargs.update(body=request)
        while True:
            try:
                res = self._es.count(**kwargs)
                break
            except ConnectionTimeout, e:
                print>>sys.stderr, e
                continue
        return res[u'count']

    def scan(self, request=None, **kwargs):
        head = {
            'client': self._es,
            'index': self._index,
            'doc_type': self._doc_type,
            'query': request
        }
        head.update(kwargs)
        return elasticsearch.helpers.scan(**head)
