from django.test import TestCase

# Create your tests here.
import requests
import json
import random
import hashlib
import string
import datetime
from .models import taskTable


def get_token(user_mail, name, time):
    """
    使用由 id, name, time 组成的明文生成相应密文
    :param id:
    :param name:
    :param time:
    :return:
    """
    data = "%s%s%s" % (user_mail, name, time)
    hash_md5 = hashlib.md5(data.encode('utf-8'))
    return hash_md5.hexdigest()


def get_authcode(length=20):
    """
    生成长度为 length 的随机字符串作为验证码
    :param length:
    :return:
    """
    char_set = list(string.digits + string.ascii_letters)
    random.shuffle(char_set)
    return "".join(char_set[:length])

def write_send_result(content):
    with open("send_status.txt","wb+") as f:
        string_write=str(datetime.datetime.now())+"  :  "+str(content)+"  \n"
        f.write(string_write)

def mail_Verification_link(name="",to_email=""):
    send_cloude_url = "http://www.sendcloud.net/webapi/mail.send_template.json"
    API_USER = "xiongxiong_test_SSjv2x"
    API_KEY = "trxmvnrrWsD9VJwg"
    token = get_token(to_email, name, datetime.datetime.now())
    authcode = get_authcode()
    base_link = "http:127.0.0.1:5000/do_verificatin?"
    link = base_link + 'token=%s&authcode=%s' % (token, authcode)

    sub_vars = {
        'to': to_email,
        'sub': {
            '%name%': [name],
            '%url%': [link],
        }
    }
    params = {
        "api_user": API_USER,
        "api_key": API_KEY,
        "template_invoke_name": "test_template_send",
        "substitution_vars": json.dumps(sub_vars),
        "from": "test1@163.com",
        "fromname": "mixiong",
        "subject": "Welcome to Shiyanlou",
        "resp_email_id": "true",
    }

    response = requests.post(url=send_cloude_url, data=params)
    write_send_result(response.text)

"""
uid = models.CharField(max_length=50)

    url = models.CharField(max_length=100)
    domain = models.CharField(max_length=50)
    keyword = models.CharField(max_length=50)
"""
allowDomains=["sust.edu.cn",]
def pushworkLimit(starturl,domain,keyword):
    if domain in starturl:
        if domain in allowDomains:
            useTask=taskTable.objects.filter(url=starturl,domain=domain,keyword=keyword)
            if useTask:
                status = False
                msg = "已发布相同的任务，请在历史记录搜索"
            else:
                status = True
                msg = "你的任务已成功发布"
        else:
            status=False
            msg="你所输入的域名不被允许，请联系管理员"
    else:
        msg="入口url不在这个网站下，请重新输入"
        status=False

    return status,msg




