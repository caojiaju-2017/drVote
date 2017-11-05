#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from CLSms import *
class SmsDataBuffer:
    def __init__(self):
        self.phone = None
        self.smsCode = None
        self.generalTime = None
        pass

    # return False 表示验证不通过，True表示通过；   0 表示记录超时或已使用  1 表示正常
    @staticmethod
    def validSms(phone,smscd,datas):
        for one in datas:
            if smscd != one.smsCode and phone != one.phone:
                continue

            # 计算时间差，看看是否超过1分钟
            nowTime = datetime.datetime.now()

            seconds = (nowTime - one.generalTime).seconds

            if seconds >= 60:
                datas.remove(one)
                return False

            datas.remove(one)
            return True
        return False
    @staticmethod
    def createSmsObj(phone):
        rtnObj = SmsDataBuffer()

        smsCode = getSmsCode()
        rtnObj.smsCode = smsCode
        rtnObj.phone = phone
        rtnObj.generalTime = datetime.datetime.now()

        return  rtnObj

    def sendMessage(self):
        stringTxt = "您的验证码是：%s。请不要把验证码泄露给其他人。"% self.smsCode
        send_sms(stringTxt,self.phone)