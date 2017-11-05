#!/usr/local/bin/python
#-*- coding:utf-8 -*-
# Author: jacky
# Time: 14-2-22 下午11:48
# Desc: 短信http接口的python代码调用示例
import httplib
import urllib
import random

host  = "106.ihuyi.com"
sms_send_uri = "/webservice/sms.php?method=Submit"

#用户名请登录用户中心->验证码、通知短信->帐户及签名设置->APIID
account  = "C05379304"
#密码 查看密码请登录用户中心->验证码、通知短信->帐户及签名设置->APIKEY
password = "e8f2b1840cfa097bb0c957e1e4a40204"

def send_sms(text, mobile):
    params = urllib.urlencode({'account': account, 'password' : password, 'content': text, 'mobile':mobile,'format':'json' })
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection(host, port=80, timeout=30)
    conn.request("POST", sms_send_uri, params, headers)
    response = conn.getresponse()
    response_str = response.read()
    conn.close()
    return response_str

def getSmsCode():
    rd = random.randint(1000, 9999)
    return "%d"%rd
if __name__ == '__main__':
    mobile = "17828061593"
    text = "您的验证码是：121254。请不要把验证码泄露给其他人。"

    #查账户余额

    #调用智能匹配模版接口发短信
    rtns = send_sms(text, mobile)
    print  rtns