#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render,render_to_response
from django.http import  HttpResponse
import json,uuid,time,base64,re
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import qrcode,urllib2
from HsShareData import *
from django.db.models import F
from DSServer.models import *

from django.template import Template, Context

appID = "wx6d45e5e461e41f06"
appsecret = "726c202ca673beff13e4bc7dd0d5d01a"
access_token = None
ticket = None

ipList = []
ipList.append('59.56.94.156')
ipList.append('110.183.55.122')
ipList.append('117.80.164.123')
ipList.append('183.202.173.49')
ipList.append('223.81.131.153')
ipList.append('122.137.254.79')
ipList.append('117.40.115.254')
ipList.append('122.137.254.233')


# http://blog.csdn.net/xiaoguo321/article/details/51483914
rtnDictGlobal={}

LastDateTime = None
Config = None

if HsShareData.lockFactorys.acquire():
    if len(HsShareData.Factorys) <= 0:
        tests = DrFactory.objects.all()
        for one in tests:
            HsShareData.Factorys.append(one)
    HsShareData.lockFactorys.release()

# if HsShareData.lockVotes.acquire():
#     if len(HsShareData.Votes) <= 0:
#         temps = DrVote.objects.all()
#
#         for one in temps:
#             HsShareData.Votes.append(one)
#     HsShareData.lockVotes.release()

if HsShareData.lockVoteRecords.acquire():
    if len(HsShareData.VoteRecords) <= 0:
        tempsT = DrVoteRecord.objects.all()

        for one in tempsT:
            HsShareData.VoteRecords.append(one)
    HsShareData.lockVoteRecords.release()

Config = DrConfig.objects.first()

IPInfo={}
LoopCountInfo={}
IPInfo22={}

first6Number=[]
LastTimes = None
class WebCenterApi(object):
    @staticmethod
    @csrf_exempt
    def CommandDispatch(req):
        command = req.GET.get('Command').upper()

        if command == 'Query_BaseInfo'.upper():
            return WebCenterApi.Query_BaseInfo(req)
        elif command  == "Set_BaseInfo".upper():
            return WebCenterApi.Set_BaseInfo(req)
        elif command == "Query_Factory".upper():
            return WebCenterApi.Query_Factory(req)
        elif command  == "Add_Factory".upper():
            return WebCenterApi.Add_Factory(req)
        elif command  == "Dele_Factory".upper():
            return WebCenterApi.Dele_Factory(req)
        elif command  == "Modi_Factory".upper():
            return WebCenterApi.Modi_Factory(req)
        elif command  == "Vote_Voting".upper():
            return WebCenterApi.Vote_Voting(req)
        elif command  == "Set_Level".upper():
            return WebCenterApi.Set_Level(req)
        elif command == "Query_Expert".upper():
            return WebCenterApi.Query_Expert(req)
        elif command  == "Add_Expert".upper():
            return WebCenterApi.Add_Expert(req)
        elif command  == "Dele_Expert".upper():
            return WebCenterApi.Dele_Expert(req)
        elif command  == "Modi_Expert".upper():
            return WebCenterApi.Modi_Expert(req)
        elif command == "View_Image".upper():
            return WebCenterApi.View_Image(req)

        elif command == "Query_UserInfo".upper():
            return WebCenterApi.Query_UserInfo(req)
        elif command == "Modi_VCount".upper():
            return WebCenterApi.Modi_VCount1(req)
        elif command == "Query_Vote_Number".upper():
            return WebCenterApi.Query_Vote_Number(req)
        elif command == "Query_AccessCount".upper():
            return WebCenterApi.Query_AccessCount(req)
    @staticmethod
    def Query_BaseInfo(request):
        global Config
        ipreques = request.META['REMOTE_ADDR']
        if ipreques in ipList:
            loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 9, "Result":0 })
            return HttpResponse(loginResut)

        config = None
        if not Config:
            Config = DrConfig.objects.first()
            config = Config
        else:
            config = Config

        if not config:
            loginResut = json.dumps({"ErrorInfo": "投票全局配置数据未设置", "ErrorId": 10002, "Result": ""})
            return HttpResponse(loginResut)



        rtnInfo={}
        rtnInfo['id'] = config.id
        rtnInfo['startdate'] = config.startdate
        rtnInfo['stopdate'] = config.stopdate
        rtnInfo['enable'] = config.enable
        rtnInfo['title'] = config.title
        rtnInfo['introduce'] = config.introduce
        rtnInfo['logoimage'] = config.logoimage

        rtnInfo['zhubanorg'] = config.zhubanorg
        rtnInfo['xiebanorg'] = config.xiebanorg
        rtnInfo['zhichiorg'] = config.zhichiorg
        rtnInfo['xiezhuorg'] = config.xiezhuorg

        rtnInfo['xiezhupinpai'] = config.xiezhupp
        rtnInfo['erweima'] = config.erweima

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": rtnInfo})
        return HttpResponse(loginResut)

    @staticmethod
    def Query_UserInfo(request):
        global IPInfo
        global ipList
        cookie = request.GET.get('cookie')
        ipreques = request.META['REMOTE_ADDR']
        # print '====',cookie
        # print '==客户IP==', real_ip
        if ipreques in ipList:
            loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 9, "Result":0 })
            return HttpResponse(loginResut)
        try:
            if HsShareData.lockVoteRecords.acquire():
                if not IPInfo.has_key(ipreques):
                    IPInfo[ipreques] = datetime.datetime.now()
                    LoopCountInfo[ipreques] = 1
                else:
                    print 'have ip info'
                    dateLast = IPInfo[ipreques]
                    nowDate = datetime.datetime.now()
                    loopCount = LoopCountInfo[ipreques]
                    if (nowDate - dateLast).seconds < 10*60 and loopCount > 100:
                        print 'ip not timeout'
                        # 如果一分钟超过100个，则加入黑名单
                        if (nowDate - dateLast).seconds < 1 * 60:
                            ipList.append(ipreques)

                        HsShareData.lockVoteRecords.release()
                        loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 1009, "Result":0 })
                        return HttpResponse(loginResut)
                    elif (nowDate - dateLast).seconds >= 10*60 :
                        IPInfo[ipreques] = datetime.datetime.now()
                        LoopCountInfo[ipreques] = 1
                    else:
                        LoopCountInfo[ipreques] = LoopCountInfo[ipreques] + 1
                HsShareData.lockVoteRecords.release()
        except:
            HsShareData.lockVoteRecords.release()

        records = DrVoteRecord.objects.filter(ucode=cookie)


        retFlag = 1

        if len(records) >0:
            record = records[0]

            currentDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            if (currentDate == record.votedate):
                retFlag = 0


        # 计算用户操作记录
        # userLastRecord = DrOpenRecord.objects.filter(fcode=cookie).order_by('opentime').last()
        # newRecord = None
        # newRecord = DrOpenRecord()
        # newRecord.fcode = cookie
        # newRecord.opentime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        # newRecord.ipaddress = real_ip
        newRecord = None
        # # time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        # if userLastRecord:
        #     opertTime = userLastRecord.opentime
        #     ipaddress = userLastRecord.ipaddress
        #     if ipaddress == real_ip:
        #         d1=datetime.datetime.strptime(opertTime, "%Y-%m-%d %H:%M:%S")
        #         d2 = datetime.datetime.now()
        #         seconds = (d2 - d1).seconds
        #
        #         if seconds > 2*60:
        #             newRecord = DrOpenRecord()
        #             newRecord.fcode = cookie
        #             newRecord.opentime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        #             newRecord.ipaddress = real_ip
        #     else:
        #         newRecord = DrOpenRecord()
        #         newRecord.fcode = cookie
        #         newRecord.opentime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #         newRecord.ipaddress = real_ip
        # else:
        #     newRecord = DrOpenRecord()
        #     newRecord.fcode = cookie
        #     newRecord.opentime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        #     newRecord.ipaddress = real_ip

        # if newRecord:
        #     commitDataList = []
        #     commitDataList.append(CommitData(newRecord, 0))
        #     # 事务提交
        #     try:
        #         result = commitCustomDataByTranslate(commitDataList)
        #
        #         if not result:
        #             print "数据库操作失败"
        #     except Exception, ex:
        #         print "数据库操作失败"

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": retFlag})
        return HttpResponse(loginResut)

    @staticmethod
    def Set_BaseInfo(request):
        global Config
        ipreques = request.META['REMOTE_ADDR']
        if ipreques in ipList:
            loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 9, "Result":0 })
            return HttpResponse(loginResut)

        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        config = None
        if not Config:
            Config = DrConfig.objects.first()
            config = Config
        else:
            config = Config

        if not config:
            config = DrConfig()

        config.startdate = postDataList['startdate']
        config.stopdate = postDataList['stopdate']
        config.enable = int(postDataList['enable'])
        config.title = postDataList['title']
        config.introduce = postDataList['introduce']

        config.zhubanorg = postDataList['zhubanorg']
        config.xiebanorg = postDataList['xiebanorg']
        config.zhichiorg = postDataList['zhichiorg']
        config.xiezhuorg = postDataList['xiezhuorg']

        if not config.logoimage or len(config.logoimage) <= 0:
            config.logoimage = uuid.uuid1().__str__().replace("-","")
        # image = postDataList['image']

        # 图片
        if len(postDataList['image']) > 0:
            imgdata = base64.b64decode(postDataList['image'])

            file = open(os.path.join(STATIC_ROOT.decode('utf-8'),'%s'%config.logoimage), 'wb')
            file.write(imgdata)
            file.close()

        if len(postDataList['imageXzpp']) > 0:
            imgdata = base64.b64decode(postDataList['imageXzpp'])

            file = open(os.path.join(os.path.join(STATIC_ROOT.decode('utf-8'),"Images"),'xbpp.png'), 'wb')
            file.write(imgdata)
            file.close()

        if len(postDataList['erWeiMa']) > 0:
            imgdata = base64.b64decode(postDataList['erWeiMa'])

            file = open(os.path.join(os.path.join(STATIC_ROOT.decode('utf-8'),"Images"),'hdj.png'), 'wb')
            file.write(imgdata)
            file.close()

        commitDataList=[]
        commitDataList.append(CommitData(config, 0))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception,ex:
            loginResut = json.dumps({"ErrorInfo":"数据库操作失败","ErrorId":99999,"Result":None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": ""})
        return HttpResponse(loginResut)

    @staticmethod
    def Query_Factory(request):
        global IPInfo
        global ipList
        # print 'Factorys.Count----------------',len(HsShareData.Factorys)
        # print 'Votes.Count----------------', len(HsShareData.Votes)
        # print 'VoteRecords.Count----------------', len(HsShareData.VoteRecords)

        pageIndex = int(request.GET.get('pageindex'))
        pageSize = int(request.GET.get('pagesize'))
        fliterStr = request.GET.get('fliter')

        # d91202a2cd0911e79a1900163e2ea800

        ipreques = request.META['REMOTE_ADDR']

        if ipreques in ipList:
            loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 9, "Result":0 })
            return HttpResponse(loginResut)

        try:
            if HsShareData.lockVoteRecords.acquire():
                if not IPInfo.has_key(ipreques):
                    IPInfo[ipreques] = datetime.datetime.now()
                    LoopCountInfo[ipreques] = 1
                else:
                    print 'have ip info'
                    dateLast = IPInfo[ipreques]
                    nowDate = datetime.datetime.now()
                    loopCount = LoopCountInfo[ipreques]
                    if (nowDate - dateLast).seconds < 10*60 and loopCount > 400:
                        print 'ip not timeout'
                        # 如果一分钟超过100个，则加入黑名单
                        if (nowDate - dateLast).seconds < 1 * 60:
                            ipList.append(ipreques)

                        HsShareData.lockVoteRecords.release()
                        loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 1009, "Result":0 })
                        return HttpResponse(loginResut)
                    elif (nowDate - dateLast).seconds >= 10*60 :
                        IPInfo[ipreques] = datetime.datetime.now()
                        LoopCountInfo[ipreques] = 1
                    else:
                        LoopCountInfo[ipreques] = LoopCountInfo[ipreques] + 1
                HsShareData.lockVoteRecords.release()
        except:
            HsShareData.lockVoteRecords.release()

        factorys = []
        # factorys = DrFactory.objects.all()
        if fliterStr and len(fliterStr) > 0:
            for one in HsShareData.Factorys:
                if fliterStr in one.name:
                    factorys.append(one)
        else:
            # factorys = DrFactory.objects.all()
            factorys = HsShareData.Factorys

        rtnDict={}
        rtnResult = []

        votes = DrVote.objects.all()
        # if HsShareData.lockVotes.acquire():
        #     votes = HsShareData.Votes
        #     votes = sorted(votes, key=lambda student: student.votecount, reverse=True)
        #     HsShareData.lockVotes.release()

        for index, one in enumerate(factorys):
            if index < pageIndex*pageSize:
                continue

            if index >= (pageIndex * pageSize + pageSize):
                break

            oneRecord = {}
            oneRecord['code'] = one.code
            oneRecord['name'] = one.name
            oneRecord['logoname'] = one.logoname
            oneRecord['externinfo1'] = one.externinfo1
            oneRecord['externinfo2'] = one.externinfo2
            oneRecord['externinfo3'] = one.externinfo3

            oneRecord['voteCount'] = 0
            for oneVote in votes:
                if oneVote.fcode == one.code:
                    oneRecord['voteCount'] = oneVote.votecount
                    break

            rtnResult.append(oneRecord)

        sortFlag = 0
        try:
            sortFlag = int(request.GET.get('sort'))
        except:
            pass

        if sortFlag == 1:
            # 排序
            sortedResult = []
            for one in rtnResult:
                count1 = one["voteCount"]

                flag = False
                for index,oneA in enumerate(sortedResult):
                    count2 = oneA["voteCount"]
                    if count1 < count2:
                        continue

                    flag = True
                    sortedResult.insert(index,one)
                    break

                if not flag:
                    sortedResult.append(one)

            rtnResult = sortedResult

        rtnDict["Datas"] = rtnResult
        rtnDict["MaxCount"] = len(factorys)
        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": rtnDict})
        return HttpResponse(loginResut)

    @staticmethod
    def Add_Factory(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        newFactory = DrFactory()
        newFactory.code = uuid.uuid1().__str__().replace("-","")
        newFactory.name = postDataList['name']
        newFactory.logoname = uuid.uuid1().__str__().replace("-","")
        newFactory.externinfo1 = postDataList['externinfo1']
        newFactory.externinfo2 = postDataList['externinfo2']
        newFactory.externinfo3 = postDataList['externinfo3']
        # 图片

        if len(postDataList['image']) > 0:
            imgdata = base64.b64decode(postDataList['image'])

            file = open(os.path.join(os.path.join(STATIC_ROOT,"factory"),'%s.jpg'% newFactory.logoname), 'wb')
            file.write(imgdata)
            file.close()


        voteNew = DrVote()
        voteNew.fcode = newFactory.code
        voteNew.votecount = 0
        commitDataList=[]
        commitDataList.append(CommitData(newFactory, 0))
        commitDataList.append(CommitData(voteNew, 0))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception,ex:
            loginResut = json.dumps({"ErrorInfo":"数据库操作失败","ErrorId":99999,"Result":None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": newFactory.code})

        return HttpResponse(loginResut)
    @staticmethod
    def Dele_Factory(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        code = postDataList['code']

        facts = DrFactory.objects.filter(code=code)

        if len(facts) == 0:
            loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 10002, "Result": ""})
            return HttpResponse(loginResut)

        imageFile = facts[0].logoname

        fvotes = DrVote.objects.filter(fcode=code)

        commitDataList = []
        commitDataList.append(CommitData(facts[0],1))
        commitDataList.append(CommitData(fvotes, 1))

        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception, ex:
            loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
            return HttpResponse(loginResut)

        # 删除图片
        if imageFile and len(imageFile) > 0:
            imageFile = os.path.join(os.path.join(STATIC_ROOT, "factory"), '%s.jpg' % imageFile)
            try:
                os.remove(imageFile)
            except:
                pass

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result":None })

        return HttpResponse(loginResut)

    @staticmethod
    def Query_AccessCount(request):
        recordCount = DrOpenRecord.objects.all().count()
        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": recordCount})
        return HttpResponse(loginResut)
        pass
    @staticmethod
    def Query_Vote_Number(request):
        global IPInfo
        global ipList

        pageIndex = int(request.GET.get('pageindex'))
        pageSize = int(request.GET.get('pagesize'))
        start = int(request.GET.get('start'))

        ipreques = request.META['REMOTE_ADDR']
        if ipreques in ipList:
            loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 9, "Result":0 })
            return HttpResponse(loginResut)

        try:
            if HsShareData.lockVoteRecords.acquire():
                if not IPInfo.has_key(ipreques):
                    IPInfo[ipreques] = datetime.datetime.now()
                    LoopCountInfo[ipreques] = 1
                else:
                    print 'have ip info'
                    dateLast = IPInfo[ipreques]
                    nowDate = datetime.datetime.now()
                    loopCount = LoopCountInfo[ipreques]
                    if (nowDate - dateLast).seconds < 10*60 and loopCount > 100:
                        print 'ip not timeout'
                        # 如果一分钟超过100个，则加入黑名单
                        if (nowDate - dateLast).seconds < 1 * 60:
                            ipList.append(ipreques)

                        HsShareData.lockVoteRecords.release()
                        loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 1009, "Result":0 })
                        return HttpResponse(loginResut)
                    elif (nowDate - dateLast).seconds >= 10*60 :
                        IPInfo[ipreques] = datetime.datetime.now()
                        LoopCountInfo[ipreques] = 1
                    else:
                        LoopCountInfo[ipreques] = LoopCountInfo[ipreques] + 1
                HsShareData.lockVoteRecords.release()
        except:
            HsShareData.lockVoteRecords.release()

        print request.GET

        # 查出前6名
        results = DrVote.objects.order_by('-votecount').all()
        #if HsShareData.lockVotes.acquire():
        #    results = HsShareData.Votes
        #    results = sorted(results, key=lambda student: student.votecount,reverse=True)
        #    # results = sorted(results, key=attrgetter('grade'), reverse=True)
        #    HsShareData.lockVotes.release()


        rtnResult = []
        for index, one in enumerate(results):
            if index < start or index - 6 < pageIndex*pageSize:
                continue

            if (index - 6) >= (pageIndex * pageSize + pageSize):
                break

            factData = None #DrFactory.objects.filter(code=one.fcode).first()

            for indexA,oneT in enumerate(HsShareData.Factorys):
                if oneT.code == one.fcode:
                    factData = oneT
                    break

            if not factData:
                continue

            renterDict={}
            renterDict["number_img"] = "/static/factory/%s.jpg" % factData.logoname
            renterDict["number_name"] = factData.name
            renterDict["number"] = index + 1
            renterDict["number_vote_count"] = one.votecount
            rtnResult.append(renterDict)

        print  rtnResult
        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": rtnResult})
        return HttpResponse(loginResut)


    @staticmethod
    def Modi_VCount(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        code = postDataList['code']
        vcount = int(postDataList['vcount'])

        # facts = DrVote.objects.filter(fcode=code)
        factoryObject = None
        findIndex = -1
        if HsShareData.lockVotes.acquire():
            HsShareData.Votes = sorted(HsShareData.Votes, key=lambda student: student.votecount, reverse=True)
            for index,one in enumerate(HsShareData.Votes):
                if one.fcode == code:
                    factoryObject = one
                    findIndex = index
                    break

            if not factoryObject :
                factoryObject = DrVote()
                factoryObject.fcode = code
                factoryObject.votecount = 0

            factoryObject.votecount = vcount
            commitDataList = []
            commitDataList.append(CommitData(factoryObject, 0))
            # 事务提交
            try:
                result = commitCustomDataByTranslate(commitDataList)

                if not result:
                    HsShareData.lockVotes.release()
                    loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                    return HttpResponse(loginResut)

                if findIndex < 0:
                    HsShareData.Votes.append(factoryObject)
                else:
                    HsShareData.Votes[findIndex] = factoryObject

                HsShareData.lockVotes.release()
            except Exception, ex:
                HsShareData.lockVotes.release()
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": None})
        return HttpResponse(loginResut)

    @staticmethod
    def Modi_Factory(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        code = postDataList['code']
        facts = DrFactory.objects.filter(code=code)

        if len(facts) != 1:
            loginResut = json.dumps({"ErrorInfo": "当前厂商数据异常", "ErrorId": 10001, "Result": None})
            return HttpResponse(loginResut)

        factory = facts[0]

        factory.name = postDataList['name']
        # factory.logoname = postDataList['logoname']
        factory.externinfo1 = postDataList['externinfo1']
        factory.externinfo2 = postDataList['externinfo2']
        factory.externinfo3 = postDataList['externinfo3']

        if len(postDataList['image']) > 0:
            # 图片
            imgdata = base64.b64decode(postDataList['image'])
            print STATIC_ROOT
            file = open(os.path.join(os.path.join("/opt/toupiao/DSServer/static","factory"),'%s.jpg'% factory.logoname), 'wb')
            file.write(imgdata)
            file.close()


        commitDataList = []
        commitDataList.append(CommitData(factory, 0))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception, ex:
            loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": None})

        return HttpResponse(loginResut)

    @staticmethod
    def Vote_Voting(request):
        global IPInfo
        global ipList
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        ucode = postDataList['ucode']
        fcode = postDataList['fcode']
        ipreques = request.META['REMOTE_ADDR']


        if ipreques in ipList:
            loginResut = json.dumps({"ErrorInfo": "", "ErrorId": 9, "Result":0 })
            return HttpResponse(loginResut)

        if fcode == "dd33cb24ccfd11e7a7de00163e2ea800":
            loginResut = json.dumps({"ErrorInfo": "技术故障，请稍后操作", "ErrorId": 1009, "Result":0 })
            return HttpResponse(loginResut)
        print ipreques

        try:
            if HsShareData.lockVoteRecords.acquire():
                if not IPInfo.has_key(ipreques):
                    IPInfo[ipreques] = datetime.datetime.now()
                    LoopCountInfo[ipreques] = 1
                else:
                    print 'have ip info'
                    dateLast = IPInfo[ipreques]
                    nowDate = datetime.datetime.now()
                    loopCount = LoopCountInfo[ipreques]
                    if (nowDate - dateLast).seconds < 10*60 and loopCount > 100:
                        print 'ip not timeout'
                        # 如果一分钟超过100个，则加入黑名单
                        if (nowDate - dateLast).seconds < 1 * 60:
                            ipList.append(ipreques)

                        HsShareData.lockVoteRecords.release()
                        loginResut = json.dumps({"ErrorInfo": "您的投票异常，同一IP投票太频繁", "ErrorId": 1009, "Result":0 })
                        return HttpResponse(loginResut)
                    elif (nowDate - dateLast).seconds >= 10*60 :
                        IPInfo[ipreques] = datetime.datetime.now()
                        LoopCountInfo[ipreques] = 1
                    else:
                        LoopCountInfo[ipreques] = LoopCountInfo[ipreques] + 1



                HsShareData.lockVoteRecords.release()
        except:
            HsShareData.lockVoteRecords.release()
        #
        # userRecords = DrVoteRecord.objects.filter(ucode=ucode)
        updateRecord = DrVoteRecord.objects.filter(ucode=ucode).first()
        # updateRecord = None
        for index ,oneRecord in enumerate(HsShareData.VoteRecords):
            if oneRecord.ucode == ucode:
                updateRecord = oneRecord
                break

        if not updateRecord:
            updateRecord = DrVoteRecord()

        userIp = None
        if request.META.has_key('HTTP_X_FORWARDED_FOR'):
            userIp = request.META['HTTP_X_FORWARDED_FOR']
        else:
            userIp = request.META['REMOTE_ADDR']

        updateRecord.ucode = ucode
        updateRecord.votedate = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        updateRecord.voteip = userIp

        # 累加厂商数据
        voteRecord = DrVote.objects.filter(fcode=fcode).first()
        if not voteRecord:
            voteRecord = DrVote()
            voteRecord.votecount = 0
            voteRecord.fcode = fcode

        count = voteRecord.votecount
        voteRecord.votecount = F('votecount') + 1
        voteRecord.save()
        commitDataList = []
        commitDataList.append(CommitData(updateRecord, 0))
        commitDataList.append(CommitData(voteRecord, 0))

        # # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)
        except Exception, ex:
            loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": count + 1})
        return HttpResponse(loginResut)

    @staticmethod
    def Set_Level(request):
        return render(request, 'home.html')

    @staticmethod
    def View_Image(request):
        imagename = request.GET.get('imagename')
        type = int(request.GET.get('type'))

        #
        imageFilePath = None
        if type == 0: # 主logo
            imageFilePath = os.path.join(STATIC_ROOT, "%s"%imagename)
        elif type == 1: # 厂商
            imageFilePath = os.path.join(os.path.join(STATIC_ROOT,"factory"), "%s.jpg" % imagename)
        elif type == 2: # 厂商
            imageFilePath = os.path.join(os.path.join(STATIC_ROOT,"expert"), "%s.jpg" % imagename)
        elif type == 3:
            imageFilePath = os.path.join(os.path.join(STATIC_ROOT, "Images"), imagename)
        if not imageFilePath:
            return HttpResponse()

        image_data = None
        try:
            image_data = open(imageFilePath, "rb").read()
        except:
            pass

        # return image_data

        return HttpResponse(image_data)


    @staticmethod
    def Query_Expert(request):
        pageIndex = int(request.GET.get('pageindex'))
        pageSize = int(request.GET.get('pagesize'))

        factorys = DrReviewExpert.objects.all()

        rtnDict={}
        rtnResult = []
        for index, one in enumerate(factorys):
            if index < pageIndex*pageSize:
                continue
            if index >= (pageIndex * pageSize + pageSize):
                break

            oneRecord = {}
            oneRecord["code"] = one.code
            oneRecord['name'] = one.name
            oneRecord['info'] = one.info
            oneRecord['faceimage'] = one.faceimage

            rtnResult.append(oneRecord)

        rtnDict["MaxCount"] = len(factorys)
        rtnDict["Datas"] = rtnResult
        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": rtnDict})
        return HttpResponse(loginResut)

    @staticmethod
    def Add_Expert(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        newExpert = DrReviewExpert()
        newExpert.code = uuid.uuid1().__str__().replace("-","")
        newExpert.name = postDataList['name']
        newExpert.faceimage = uuid.uuid1().__str__().replace("-","")
        newExpert.info = postDataList['info']
        # 图片

        if len(postDataList['image']) > 0:
            imgdata = base64.b64decode(postDataList['image'])

            file = open(os.path.join(os.path.join(STATIC_ROOT,"expert"),'%s.jpg'% newExpert.faceimage), 'wb')
            file.write(imgdata)
            file.close()


        commitDataList=[]
        commitDataList.append(CommitData(newExpert, 0))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception,ex:
            loginResut = json.dumps({"ErrorInfo":"数据库操作失败","ErrorId":99999,"Result":None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": newExpert.code})

        return HttpResponse(loginResut)
    @staticmethod
    def Dele_Expert(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        code = postDataList['code']

        experts = DrReviewExpert.objects.filter(code=code)

        if len(experts) == 0:
            loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 10002, "Result": ""})
            return HttpResponse(loginResut)

        commitDataList = []
        commitDataList.append(CommitData(experts[0],1))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception, ex:
            loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
            return HttpResponse(loginResut)

        # 删除图片
        imageFile = experts[0].faceimage
        if imageFile and len(imageFile) > 0:
            imageFile = os.path.join(os.path.join(STATIC_ROOT, "expert"), '%s.jpg' % imageFile)
            try:
                os.remove(imageFile)
            except:
                pass

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result":None })

        return HttpResponse(loginResut)

    @staticmethod
    def Modi_Expert(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        code = postDataList['code']
        facts = DrReviewExpert.objects.filter(code=code)

        if len(facts) != 1:
            loginResut = json.dumps({"ErrorInfo": "数据异常", "ErrorId": 10001, "Result": None})
            return HttpResponse(loginResut)

        factory = facts[0]

        factory.name = postDataList['name']
        # factory.logoname = postDataList['logoname']
        factory.info = postDataList['info']

        if len(postDataList['image']) > 0:
            # 图片
            imgdata = base64.b64decode(postDataList['image'])

            file = open(os.path.join(os.path.join(STATIC_ROOT,"expert"),'%s.jpg'% factory.faceimage), 'wb')
            file.write(imgdata)
            file.close()


        commitDataList = []
        commitDataList.append(CommitData(factory, 0))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception, ex:
            loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": None})

        return HttpResponse(loginResut)

    @staticmethod
    @csrf_exempt
    def goHome(request):
        global Config
        isMangeFlag = 0
        try:
            isMangeFlag = int(request.GET.get('mangeflag'))
        except:
            pass
        if isMangeFlag != 1 and (not HsShareData.IsDebug)  and not checkMobile(request):
            return HttpResponse("仅能通过手机操作")


        config = None
        if not Config:
            Config = DrConfig.objects.first()
            config = Config
        else:
            config = Config
        renterDict = {}
        renterDict['title'] = config.title
        renterDict['vote_intro'] = "      " + config.introduce.replace("<br>","\n").replace("&nbsp"," ")
        renterDict['main_logo'] = "/static/%s" % config.logoimage
        renterDict['start_date'] = config.startdate
        renterDict['stop_date'] = config.stopdate
        renterDict['ZhuBanOrg'] = config.zhubanorg
        renterDict['ChengBanOrg'] = config.xiebanorg
        renterDict['ZhiChiOrg'] = config.zhichiorg
        renterDict['XieZhuOrg'] = config.xiezhuorg
        return render(request, 'vote_home.html',renterDict )

    @staticmethod
    @csrf_exempt
    def openIntroduce(request):
        global Config
        if not HsShareData.IsDebug  and not checkMobile(request):
            return HttpResponse("仅能通过手机操作")

        config = None
        if not Config:
            Config = DrConfig.objects.first()
            config = Config
        else:
            config = Config
        renterDict = {}
        renterDict['title'] = config.title
        renterDict['vote_intro'] = "      " + config.introduce.replace("<br>","\n").replace("&nbsp"," ")
        renterDict['main_logo'] = "/static/%s" % config.logoimage
        renterDict['start_date'] = config.startdate
        renterDict['stop_date'] = config.stopdate

        return render(request, 'vote_introduce.html',renterDict )

    @staticmethod
    @csrf_exempt
    def openExpet(request):
        global Config
        if not HsShareData.IsDebug  and not checkMobile(request):
            url = "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + request.META['QUERY_STRING']
            img = qrcode.make(url)
            img.save(os.path.join(os.path.join(STATIC_ROOT,"Images"),"erweima_img.png"))
            return render(request, 'vote_notice.html',{"erweima_img":"/static/Images/erweima_img.png"})

        config = None
        if not Config:
            Config = DrConfig.objects.first()
            config = Config
        else:
            config = Config
        renterDict = {}
        renterDict['title'] = config.title
        renterDict['vote_intro'] = "      " + config.introduce.replace("<br>","\n").replace("&nbsp"," ")
        renterDict['main_logo'] = "/static/%s" % config.logoimage
        return render(request, 'vote_expert.html',renterDict )

    @staticmethod
    @csrf_exempt
    def shareToFriend(request):
        global rtnDictGlobal
        global LastDateTime
        rtnDict = {}
        import time

        url = request.GET.get('url')

        print "shareToFriend===>",url

        nonceStr = 'Zfdf09i'
        timesnamp = int(time.time())
        time2 = datetime.datetime.now()
        if rtnDictGlobal.has_key("timeStamp"):
            print 'not First apply tickets'
            valueOld = rtnDictGlobal.has_key("timeStamp")
            time1 = LastDateTime

            sepSeconds = (time2 - time1).seconds

            print 'time2 - time1 =======================================> ', sepSeconds
            if sepSeconds > 3600:
                rtnDict['timeStamp'] = timesnamp
                rtnDict['nonceStr'] = nonceStr
                rtnDict['signature'] = WebCenterApi.getSignature(appID, appsecret, url, timesnamp, nonceStr)
                rtnDict['appId'] = 'wx6d45e5e461e41f06'
                # print rtnDictGlobal
                rtnDictGlobal = rtnDict
                LastDateTime = time2
                # print rtnDictGlobal
                print 'Timeout'
            else:
                print 'Not Timeout'

        else:
            print 'First apply tickets'
            rtnDict['timeStamp'] = timesnamp
            rtnDict['nonceStr'] = nonceStr
            rtnDict['signature'] = WebCenterApi.getSignature(appID, appsecret, url, timesnamp, nonceStr)
            rtnDict['appId'] = 'wx6d45e5e461e41f06'
            rtnDictGlobal = rtnDict
            LastDateTime = time2

        print '=============>',rtnDictGlobal
        loginResut = json.dumps(rtnDictGlobal)
        return HttpResponse(loginResut)

    @staticmethod
    def getAccessToken(appid,appsecret):
        global access_token
        # WEIXIN_JSAPI_TICKET_URL = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=ACCESS_TOKEN&type=jsapi";
        # access_token = mapToken.get("accessToken")
        if access_token == None:
            url = "https://api.weixin.qq.com" + "/cgi-bin/token?grant_type=client_credential&appid="+appid+"&secret="+appsecret;

            # menuJsonStr = HttpUtil.get(url);
            # 定义字典
            try:
                req = urllib2.Request(url)
                res = urllib2.urlopen(req)
                res = res.read()

                print '===getAccessToken===>',res
                resDict = json.loads(res)
                access_token = resDict['access_token']
            except :
                access_token = None

        return access_token

    @staticmethod
    def getJsapiTicket(accessToken):
        global ticket
        if ticket == None:
            print "===>",access_token
            url = None
            try:
                url = "https://api.weixin.qq.com" + "/cgi-bin/ticket/getticket?access_token="+accessToken+"&type=jsapi"
            except:
                return None
            # menuJsonStr = HttpUtil.get(url);
            # type = new TypeToken < Map < String, Object >> () {}.getType();
            #  Map < Object, Object > ticketInfo = new Gson().fromJson(menuJsonStr, type);
            try:
                req = urllib2.Request(url)
                res = urllib2.urlopen(req)
                res = res.read()

                print '===getJsapiTicket===>', res

                resJson = json.loads(res)
                ticket = resJson['ticket']
            except:
                ticket = None

        print 'tickes====',ticket
        return ticket

    @staticmethod
    def getSignature(appid,appscret,url,timesnamp,noncestr):
        accessToken = WebCenterApi.getAccessToken(appid, appscret)
        jsapi_ticket = WebCenterApi.getJsapiTicket(accessToken)
        signValue = "jsapi_ticket=" + jsapi_ticket + "&noncestr=" + noncestr + "&timestamp=" + str(timesnamp) + "&url=" + url

        import hashlib
        signature = hashlib.sha1(signValue).hexdigest()
        return signature
    pass

    @staticmethod
    @csrf_exempt
    def openVoteNumber(request):
        global Config
        global first6Number
        global LastTimes
        if not HsShareData.IsDebug  and not checkMobile(request):
            url = "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + request.META['QUERY_STRING']
            img = qrcode.make(url)
            img.save(os.path.join(os.path.join(STATIC_ROOT,"Images"),"erweima_img.png"))
            return render(request, 'vote_notice.html',{"erweima_img":"/static/Images/erweima_img.png"})

        config = None
        if not Config:
            Config = DrConfig.objects.first()
            config = Config
        else:
            config = Config
        renterDict = {}
        renterDict['title'] = config.title
        renterDict['vote_intro'] = "      " + config.introduce.replace("<br>","\n").replace("&nbsp"," ")
        renterDict['main_logo'] = "/static/%s" % config.logoimage


        # 查出前6名
        # if len(first6Number) == 0:
        #     first6Number = (DrVote.objects.order_by('-votecount').all())[:10]
        #     LastTimes = datetime.datetime.now()
        # else:
        #     nowT = datetime.datetime.now()
        #     if (nowT - LastTimes).seconds > 5*60:
        #         first6Number = (DrVote.objects.order_by('-votecount').all())[:10]
        results = (DrVote.objects.order_by('-votecount').all())[:10]
        for index, one in enumerate(results):
            print one.fcode

            for oneFact in HsShareData.Factorys:
                if oneFact.code ==one.fcode:
                    factData = oneFact
                    break

            if not factData:
                continue

            if index == 0:
                renterDict["number1_img"] = "/static/factory/%s.jpg"%factData.logoname
                renterDict["number1_name"] = factData.name
                renterDict["number1_vote_count"] = one.votecount
            elif index == 1:
                renterDict["number2_img"] = "/static/factory/%s.jpg"%factData.logoname
                renterDict["number2_name"] = factData.name
                renterDict["number2_vote_count"] = one.votecount
            elif index == 2:
                renterDict["number3_img"] = "/static/factory/%s.jpg"%factData.logoname
                renterDict["number3_name"] = factData.name
                renterDict["number3_vote_count"] = one.votecount
            elif index == 3:
                renterDict["number4_img"] = "/static/factory/%s.jpg"%factData.logoname
                renterDict["number4_name"] = factData.name
                renterDict["number4_vote_count"] = one.votecount
            elif index == 4:
                renterDict["number5_img"] = "/static/factory/%s.jpg"%factData.logoname
                renterDict["number5_name"] = factData.name
                renterDict["number5_vote_count"] = one.votecount
            elif index == 5:
                renterDict["number6_img"] = "/static/factory/%s.jpg"%factData.logoname
                renterDict["number6_name"] = factData.name
                renterDict["number6_vote_count"] = one.votecount
            pass
        return render(request, 'vote_number.html',renterDict )

def getPostData(request):
    postDataList = {}
    if request.method == 'POST':
        for key in request.POST:
            try:
                postDataList[key] = request.POST.getlist(key)[0]
            except:
                pass

    import json
    if not postDataList or len(postDataList) == 0:
        try:
            bodyTxt = request.body
            postDataList = json.loads(bodyTxt)
        except Exception,ex:
            pass

    return  postDataList

def commitCustomDataByTranslate(objHandles):
    with transaction.atomic():
        for oneObject in objHandles:
            if not oneObject.dbHandle:
                continue

            try:
                if oneObject.operatorType == 0:
                    oneObject.dbHandle.save()
                elif oneObject.operatorType == 1:
                    oneObject.dbHandle.delete()
            except Exception,ex:
                return  False

    return True


#判断网站来自mobile还是pc
def checkMobile(request):
    """
    demo :
        @app.route('/m')
        def is_from_mobile():
            if checkMobile(request):
                return 'mobile'
            else:
                return 'pc'
    :param request:
    :return:
    """
    userAgent = request.META.get('HTTP_USER_AGENT', None)
    # userAgent = request.headers['User-Agent']
    # userAgent = env.get('HTTP_USER_AGENT')

    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(userAgent) != None:
        return True
    user_agent = userAgent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False
