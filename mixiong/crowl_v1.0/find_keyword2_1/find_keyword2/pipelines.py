# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import csv
import codecs
from twisted.enterprise import adbapi
import pymysql
import datetime
class FindKeyword2Pipeline(object):
    def process_item(self, item, spider):
        return item



class MysqlTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    @classmethod
    def from_settings(cls,settings):
        conn_inf=dict(
            host=settings["MYSQL_HOST"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWD"],
            database=settings["MYSQL_DBNAME"],
            charset="utf8",
            use_unicode=True,
        )
        dbpool=adbapi.ConnectionPool("pymysql",**conn_inf)
        return cls(dbpool)

    def process_item(self,item,spider):
        query=self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error)

    def handle_error(self,failure):
        print (failure)

    def do_insert(self,cursor,item):
        """
| id           | int(11)      | NO   | PRI | NULL    | auto_increment |
| url          | varchar(100) | NO   |     | NULL    |                |
| keyWordNum   | int(11)      | NO   |     | NULL    |                |
| modifiedTime | varchar(50)  | NO   |     | NULL    |                |
| startTime    | datetime     | NO   |     | NULL    |                |
| task_id      | int(11)      | NO   | MUL | NULL
        """
        item = dict(item)

        sql = """
                   insert into spiderKey(url,keyWordNum,modifiedTime,startTime,task_id) values(%s,%s,%s,%s,%s);
               """
        cursor.execute(sql, (item.get('url'), item.get('keyWordNum'), item.get('modifiedTime'), item.get('startTime'),item.get("task_id")))
        # keyword ,find_num,url,modified_time