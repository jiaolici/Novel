# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    author=scrapy.Field()
    name=scrapy.Field()
    intr=scrapy.Field()
    cover=scrapy.Field()
    novel_type=scrapy.Field()
    last_update_chapter=scrapy.Field()
    last_update_time = scrapy.Field()
    status = scrapy.Field()
    source = scrapy.Field()
    novel_url = scrapy.Field()