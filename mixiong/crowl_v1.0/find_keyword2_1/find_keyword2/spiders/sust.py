# -*- coding: utf-8 -*-
import scrapy
import re
import sys
import os
from fake_useragent import UserAgent
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append('..')
from  items import FindKeyword2Item
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from urllib import parse
import datetime

parameter_num=len(sys.argv[1:])
if parameter_num<3:
    exit()
start_url=sys.argv[1]
site_domains=sys.argv[2]
keyword=sys.argv[3]
taskId=sys.argv[4]

#
# start_url="http://www.sust.edu.cn/xxgk/xrld.htm"
# site_domains="sust.edu.cn"
# keyword= "陕西科技大学"
now_datatime=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class SustSpider(scrapy.Spider):
    name="sust1"
    global start_url
    global site_domains

    allowed_domains=[site_domains]
    start_urls=[start_url]

    def parse(self, response):
        content=FindKeyword2Item()
        """
    url=scrapy.Field()
    keyWordNum=scrapy.Field()
    modifiedTime=scrapy.Field()
    startTime=scrapy.Field()
    task_id=scrapy.Field()
        """
        global keyword

        html=response.body
        find_result=re.findall(keyword,html.decode('utf-8',"ignore"))
        find_num=len(find_result)

        if find_num!=0:
            modified_time=response.headers.get("Last-Modified",None)
            content["url"] =response.url
            content["keyWordNum"] =find_num
            content["startTime"] =now_datatime
            content["task_id"] = taskId

            if modified_time!=None:
                content["modifiedTime"] =modified_time.decode('ascii')

            yield content

        user_object = UserAgent()
        header = {
            "User-Agent": user_object.chrome
        }
        try:
            links=response.xpath('//@href')
        except Exception  as e:
            pass
        else:
            if len(links)!=0:
                for link in links:
                    each_link=link.extract()
                    if each_link and "javascript" not in each_link:
                        each_link=parse.urljoin(response.url,each_link)
                        yield scrapy.Request(url=each_link,callback=self.parse,headers=header)

                        # yield scrapy.Request(url=each_link,callback=self.parse)

if __name__=="__main__":
    pro=CrawlerProcess(get_project_settings())
    pro.crawl("sust1")
    pro.start()
#     pass
#     python sust.py   http://www.sust.edu.cn  sust.edu.cn "陕西科技大学"
