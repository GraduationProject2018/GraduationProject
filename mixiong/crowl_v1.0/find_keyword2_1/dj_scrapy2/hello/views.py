#coding=utf-8
from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse,FileResponse
import os
import sys
import json
sys.path.append('..')

from hello.models import taskTable,spiderkeyTable
import codecs
from  .tasks import spider_key
from .other import mail_Verification_link,pushworkLimit
import datetime





def search(request):
    """

     "starturl": "http://www.sust.edu.cn",
        "demols": "sust.edu.cn",
        "keyword": "陕西科技大学",
        "uid":"1",
    :param request:
    :return:
    """
    if request.method=="POST":
        request_body=json.loads(request.body)
        print (request_body)
        starturl =request_body.get("starturl")
        domain = request_body.get("demols")
        keyword = request_body.get('keyword')
        uid=request_body.get('uid')

        status=True
        msg=""

        limitResult,msg=pushworkLimit(starturl,domain,keyword)
        if limitResult:
            taskObj = taskTable(
                uid=uid,
                url=starturl,
                domain=domain,
                keyword=keyword,
                taskCreateDate=datetime.datetime.now(),
                subscribeStatus=0,
                status=0,
            )
            taskObj.save()
            spider_key.delay(starturl,domain,keyword,str(taskObj.id))
        else:
            status=False
        return HttpResponse(json.dumps({"status":status,"msg":msg}))


def setSubscribe(request):
    if request.method=="POST":
        request_body = json.loads(request.body)
        taskid=request_body.get('taskid')

        taskObj=taskTable.objects.get(id=taskid)
        taskObj.subscribeStatus=1
        taskObj.save()

        return HttpResponse(json.dumps({"status":True}))

def getHistoryList(request):
    if request.method=="POST":
        request_body=json.loads(request.body)
        uid=request_body.get('uid')
        # subscribe = request_body.get('subscribe')

        taskList=taskTable.objects.filter(uid=uid)
        status=True
        data=[]

        if taskList:
            for taskObj in taskList:
                taskdate = datetime.datetime.strftime(taskObj.taskCreateDate, "%Y-%m-%d %H:%M:%S")
                onedata = {
                    "taskid": taskObj.id,
                    "startUrl": taskObj.url,
                    "domain": taskObj.domain,
                    "keyword": taskObj.keyword,
                    "taskCreateDate": taskdate,
                }
                data.append(onedata)
        else:
            status=False

        return HttpResponse(json.dumps({"status":status,"data":data}))


def getSubscribeList(request):
    if request.method=="POST":
        request_body=json.loads(request.body)
        uid=request_body.get('uid')
        subscribe = request_body.get('subscribe')

        taskList=taskTable.objects.filter(uid=uid,subscribeStatus=subscribe)
        status=True
        data=[]

        if taskList:
            for taskObj in taskList:
                taskdate = datetime.datetime.strftime(taskObj.taskCreateDate, "%Y-%m-%d %H:%M:%S")
                onedata = {
                    "taskid": taskObj.id,
                    "startUrl": taskObj.url,
                    "domain": taskObj.domain,
                    "keyword": taskObj.keyword,
                    "taskCreateDate": taskdate,
                }
                data.append(onedata)
        else:
            status=False

        return HttpResponse(json.dumps({"status":status,"data":data}))


def showResult(request):
    if request.method=="POST":
        request_body=json.loads(request.body)
        taskid=request_body.get('taskid')

        taskObj=taskTable.objects.get(id=taskid)
        ##默认返回10条数据 按照num大小排序
        getNum=5
        spiderResult=spiderkeyTable.objects.filter(task_id=taskid)
        if spiderResult.count()<getNum:
            getNum=spiderResult.count()

        spiderResult=spiderResult.order_by("-keyWordNum")[0:getNum]
        status=True
        data={}
        urls=[]
        if spiderResult:
            keyWord=taskObj.keyword
            domain=taskObj.domain

            for  onespider in spiderResult:
                url=onespider.url
                num=onespider.keyWordNum
                modifiedDate = datetime.datetime.strptime(onespider.modifiedTime,"%a, %d %b %Y %H:%M:%S %Z")
                modifiedDateStr=datetime.datetime.strftime(modifiedDate, "%Y-%m-%d %H:%M:%S")
                urls.append({"url":url,"num":num,"modifiedDate":modifiedDateStr})

            data={
                "keyWord":keyWord,
                "domain":domain,
                "urls":urls,
            }
        else:
            status=False

        return HttpResponse(json.dumps({"status":status,"data":data}))
