# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

"""
"""
class FindKeyword2Item(scrapy.Item):

    url=scrapy.Field()
    keyWordNum=scrapy.Field()
    modifiedTime=scrapy.Field()
    startTime=scrapy.Field()
    task_id=scrapy.Field()
    pass
