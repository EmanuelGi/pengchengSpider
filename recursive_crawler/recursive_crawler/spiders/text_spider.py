import scrapy
from urlparse import urlparse
import time
import random

from scrapy.spiders import Spider
from scrapy.selector import Selector
from recursive_crawler.items import Med
from scrapy.exporters import JsonLinesItemExporter
from scrapy_redis.spiders import RedisSpider

import html2text
import redis
import json


class RecursiveSpider(RedisSpider):
    name = 'RecursiveSpider'
    redis_key = 'to_crawl'

    def __init__(self, *args, **kwargs):
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        self.redis_batch_size = 200
        super(RecursiveSpider, self).__init__(*args, **kwargs)

    def get_domain(self, response):
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        return domain

    def get_same_domain_URL(self, domain, response):
        try:
            sel = Selector(response)
            urls = set([response.urljoin(href.extract()) for href in sel.xpath('//@href')])
            urls_same_domain = [url for url in urls if url.startswith(domain)]
            return urls_same_domain
        except AttributeError:
            pass

    def get_page_items(self, response):
        title = response.css('title::text').extract()
        if not title:
            title = ''
        else:
            title = title[0].encode("utf-8")

        description = response.xpath(
            "//meta[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')\
            ,'description')]/@content").extract()
        if not description:
            description = ''
        else:
            description = description[0].encode("utf-8")

        keywords = response.xpath(
            "//meta[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')\
            ,'keywords')]/@content").extract()
        if not keywords:
            keywords = ''
        else:
            keywords = keywords[0].encode("utf-8")

        sel = scrapy.Selector(response)
        sample = sel.xpath("/*").extract()[0]
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        content = converter.handle(sample).encode('utf-8')

        med = Med()
        med['url'] = response.url
        med['title'] = title
        med['description'] = description
        med['keywords'] = keywords
        med['content'] = content
        return med

    def parse(self, response):
        yield scrapy.Request(response.url, callback=self.parse_links_follow_next_page)

    def parse_links_follow_next_page(self, response):
        item = self.get_page_items(response)
        yield item
        # domain = self.getDomain(response)
        if response.meta.get('domain'):
            domain = response.meta.get('domain')
        else:
            domain = self.get_domain(response)
        next_page_urls = self.get_same_domain_URL(domain, response)
        if next_page_urls:
            for url in next_page_urls:
                yield scrapy.Request(url, self.parse_links_follow_next_page, meta={'domain': self.get_domain(response)})
