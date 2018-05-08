# from django.shortcuts import render
#
# # Create your views here.
# from django.http import HttpResponse,StreamingHttpResponse,FileResponse
# from django.shortcuts import render
# import os
# import sys
# import json
# sys.path.append('..')
# from hello.models import User
# #from hello.models import Test
# from hello.models import Spider_key
# import codecs
# from  .tasks import spider_key
#
# def register(request):
#
#     if request.method=="POST":
#         request_body=json.loads(request.body)
#         username=request_body["username"]
#         password=request_body["password"]
#         mail=request_body["mail"]
#         print(username,password,mail)
#         ##判断用户名或者email是否存在
#         db_user=User.objects.filter(username=username)
#         db_mail=User.objects.filter(mail=mail)
#         result="0"
#         if db_user:
#             result="1"
#         elif db_mail:
#             result = "2"
#         else:
#             user_obj=User(username=username,password=password,mail=mail)
#             user_obj.save()
#         return HttpResponse(json.dumps({"status":result}))
#  #   if request.method=="GET":
#  #       return render(request,'register.html')
#
# def login(request):
#     if request.method=="POST":
#         request_body=json.loads(request.body)
#         password=request_body["password"]
#         mail=request_body["mail"]
#
#         result = "0"
#         user="None"
#         ##判断用户名或者email是否存在
#         # db_user=User.objects.filter(username=username)
#         db_mail=User.objects.filter(mail=mail)
#         if db_mail:
#             db_obj = User.objects.get(mail=mail)
#             if db_obj.password!=password:
#                 result="2"
#             else:
#                 user=db_obj.username
#         else:
#             result="1"
#         return HttpResponse(json.dumps({"status":result,"username":user}))
# #    if request.method=="GET":
# #        return render(request,'login.html')
#
# def search(request):
#     if request.method=="POST":
#         request_body=json.loads(request.body)
#         starturl =request_body["starturl"]
#         demols = request_body["demols"]
#         keyword = request_body['keyword']
#         user=request_body['user']
#         #starturl = request_body("starturl")
#         #demols = request_body("demols")
#         #keyword = request_body('keyword')
#         #user=request_body('user')
#         #dirname=os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
#         #comment_path=os.path.join(dirname,"find_keyword2/spiders/sust.py")
#         #log_dir=os.path.join(dirname,"dj_scrapy2/other/scrapy.log")
#         # comment="python /mnt/hgfs/centos_share/python/auto_python/find_keyword2/find_keyword2/spiders/sust.py   "+starturl+ "   " +demols+ "  " +keyword
#         #comment="python "+ comment_path +  "  "   + starturl + "   " + demols + "  " + keyword + "   " + user+" >> "+log_dir +"  &"
#
#         # print (comment)
#         #os.system(comment)
#         spider_key.delay(starturl,demols,keyword,user)
#         return HttpResponse(json.dumps({"status":"0"}))
# #    if request.method=="GET":
# #        return render(request, 'hello.html')
#
# def showResult(request):
#     if request.method=="POST":
#         request_body=json.loads(request.body)
#         user=request_body["user"]
#         keyword=request_body["keyword"]
#         create_task_datetime=request_body["create_task_datetime"]
#
#         result_list=[]
#         show_content=Spider_key.objects.filter(user=user,keyword=keyword,create_task_time=create_task_datetime).order_by('-find_num')[0:10]
#         if len(show_content)!=0:
#             for each_show in show_content:
#                 keyword=each_show.keyword
#                 site=each_show.site
#                 url=each_show.url
#                 num=each_show.find_num
#                 result_list.append({"keyword":keyword,"site":site,"url":url,"num":num})
#             return HttpResponse(json.dumps(result_list))
#         else:
#             return HttpResponse(json.dumps({"keyword":None,"site":None,"url":None,"num":None}))
#
# def show(request):
#     if request.method=="POST":
#         request_body=json.loads(request.body)
#         #print (request_body)
#         user=request_body["user"]
#         objs=Spider_key.objects.filter(user=user)
#         result=[]
#         delete_same=[]
#
#         for each in objs:
#             keyword=each.keyword
#             date_time=each.create_task_time
#             string_time=keyword+date_time
#             if string_time not in delete_same:
#                 delete_same.append(string_time)
#                 result.append({"keyword":keyword,"date_time":date_time})
#
#         return HttpResponse(json.dumps(result))
#
#
#
# #def test(request):
# #    if request.method=="POST":
# #        # num =request_body("num")
# #        age = request_body("age")
# #        name = request_body("name")
# #
# #        show_content = Test.objects.filter(name=name, age=age).order_by('-num')[0:1]
# #        result_list=[]
# #
# #        for i in show_content:
# #            result_list.append({"name":i.name,"age":i.age,"num":i.num})
# #        return HttpResponse(json.dumps(result_list))
# #    else:
# #        return render(request,"test.html")
