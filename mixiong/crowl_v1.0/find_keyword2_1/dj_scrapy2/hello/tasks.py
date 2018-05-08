#!/usr/bin/python
from celery import task
import os
import datetime


@task
def  spider_key(starturl,domain,keyword,taskId):

        dirname=os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
        comment_path=os.path.join(dirname,"find_keyword2/spiders/sust.py")
        log_dir=os.path.join(dirname,"dj_scrapy2/other/scrapy.log")
        comment="python "+ comment_path +  "  "   + starturl + "   " + domain + "  " + keyword + "   " + taskId+" >> "+log_dir +"  &"
        os.system(comment)
        return "spider start"
