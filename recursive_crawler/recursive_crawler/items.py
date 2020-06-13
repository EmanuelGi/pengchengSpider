# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.loader.processors import TakeFirst
from scrapy.loader.processors import Join


class Med(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    keywords = scrapy.Field()
    content = scrapy.Field()


class MedLoader(ItemLoader):
    default_item_class = Med
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    default_selector_class = Join()

