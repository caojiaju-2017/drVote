#!/usr/bin/env python
# -*- coding: utf-8 -*-

from DSServer.WX.wzhifuSDK import *
from pymongo import MongoClient
import re

def InvokeWXInterface():
    prpareOrder = UnifiedOrder_pub()
    prpareOrder.parameters["out_trade_no"] = "20170824125346"
    prpareOrder.parameters["body"] = "预付款单接口测试"
    prpareOrder.parameters["total_fee"] = "1"
    prpareOrder.parameters["notify_url"] = "http://www.weixin.qq.com/wxpay/pay.php"
    prpareOrder.parameters["trade_type"] = "APP"


    print prpareOrder.getPrepayId()


def testMongo():
    client = MongoClient('www.h-sen.com', 27017)

    db = client['TenderDb']
    tenderDatas = db["ZhaoBiao"]

    queryResult = tenderDatas.find({'$or':[{'ProjectName': re.compile("系统")},{'ProjectName': re.compile("计算机")}]})

    print queryResult.count()
    pass
if __name__ == '__main__':
    testMongo()