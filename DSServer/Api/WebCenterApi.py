#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render,render_to_response
from django.http import  HttpResponse
import json,uuid,time,base64,re
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import qrcode
from HsShareData import *

from DSServer.models import *

from django.template import Template, Context

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
            return WebCenterApi.Modi_VCount(req)

    @staticmethod
    def Query_BaseInfo(request):
        config = DrConfig.objects.first()

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
        cookie = request.GET.get('cookie')
        print '====',cookie
        records = DrVoteRecord.objects.filter(ucode=cookie)

        retFlag = 1

        if len(records) >0:
            record = records[0]

            currentDate = time.strftime('%Y-%m-%d', time.localtime(time.time()))

            if (currentDate == record.votedate):
                retFlag = 0



        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": retFlag})
        return HttpResponse(loginResut)

    @staticmethod
    def Set_BaseInfo(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        config = DrConfig.objects.first()
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
        pageIndex = int(request.GET.get('pageindex'))
        pageSize = int(request.GET.get('pagesize'))
        fliterStr = request.GET.get('fliter')

        factorys = None
        if fliterStr and len(fliterStr) > 0:
            factorys= DrFactory.objects.filter(name__contains=fliterStr)
        else:
            factorys = DrFactory.objects.all()

        rtnDict={}
        rtnResult = []

        votes = DrVote.objects.all()
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


        commitDataList=[]
        commitDataList.append(CommitData(newFactory, 0))
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
    def Modi_VCount(request):
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        code = postDataList['code']
        vcount = int(postDataList['vcount'])

        facts = DrVote.objects.filter(fcode=code)
        factoryObject = None
        if len(facts) > 1:
            loginResut = json.dumps({"ErrorInfo": "当前厂商数据异常", "ErrorId": 10001, "Result": None})
            return HttpResponse(loginResut)
        elif len(facts) == 1:
            factoryObject = facts[0]
        else:
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
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception, ex:
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

            file = open(os.path.join(os.path.join(STATIC_ROOT,"factory"),'%s.jpg'% factory.logoname), 'wb')
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
        # 提取post数据
        postDataList = {}
        postDataList = getPostData(request)

        ucode = postDataList['ucode']
        fcode = postDataList['fcode']

        #
        userRecords = DrVoteRecord.objects.filter(ucode=ucode)
        updateRecord = None
        if len(userRecords) > 0:
            updateRecord = userRecords[0]
        else:
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
        voteRecords = DrVote.objects.filter(fcode=fcode)
        voteRecord = None
        if len(voteRecords) > 0:
            voteRecord = voteRecords[0]
        else:
            voteRecord = DrVote()
            voteRecord.votecount = 0

        voteRecord.fcode = fcode
        voteRecord.votecount = voteRecord.votecount + 1

        commitDataList = []
        commitDataList.append(CommitData(updateRecord, 0))
        commitDataList.append(CommitData(voteRecord, 0))
        # 事务提交
        try:
            result = commitCustomDataByTranslate(commitDataList)

            if not result:
                loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
                return HttpResponse(loginResut)
        except Exception, ex:
            loginResut = json.dumps({"ErrorInfo": "数据库操作失败", "ErrorId": 99999, "Result": None})
            return HttpResponse(loginResut)

        loginResut = json.dumps({"ErrorInfo": "操作成功", "ErrorId": 200, "Result": voteRecord.votecount})

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
        isMangeFlag = 0
        try:
            isMangeFlag = int(request.GET.get('mangeflag'))
        except:
            pass
        if isMangeFlag != 1 and (not HsShareData.IsDebug)  and not checkMobile(request):
            url = "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + request.META['QUERY_STRING']
            img = qrcode.make(url)
            img.save(os.path.join(os.path.join(STATIC_ROOT,"Images"),"erweima_img.png"))
            return render(request, 'vote_notice.html',{"erweima_img":"/static/Images/erweima_img.png"})

        config = DrConfig.objects.first()
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
        if not HsShareData.IsDebug  and not checkMobile(request):
            url = "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + request.META['QUERY_STRING']
            img = qrcode.make(url)
            img.save(os.path.join(os.path.join(STATIC_ROOT,"Images"),"erweima_img.png"))
            return render(request, 'vote_notice.html',{"erweima_img":"/static/Images/erweima_img.png"})

        config = DrConfig.objects.first()
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
        if not HsShareData.IsDebug  and not checkMobile(request):
            url = "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + request.META['QUERY_STRING']
            img = qrcode.make(url)
            img.save(os.path.join(os.path.join(STATIC_ROOT,"Images"),"erweima_img.png"))
            return render(request, 'vote_notice.html',{"erweima_img":"/static/Images/erweima_img.png"})

        config = DrConfig.objects.first()
        renterDict = {}
        renterDict['title'] = config.title
        renterDict['vote_intro'] = "      " + config.introduce.replace("<br>","\n").replace("&nbsp"," ")
        renterDict['main_logo'] = "/static/%s" % config.logoimage
        return render(request, 'vote_expert.html',renterDict )

    @staticmethod
    @csrf_exempt
    def openVoteNumber(request):
        if not HsShareData.IsDebug  and not checkMobile(request):
            url = "http://" + request.META['HTTP_HOST'] + request.META['PATH_INFO'] + request.META['QUERY_STRING']
            img = qrcode.make(url)
            img.save(os.path.join(os.path.join(STATIC_ROOT,"Images"),"erweima_img.png"))
            return render(request, 'vote_notice.html',{"erweima_img":"/static/Images/erweima_img.png"})

        config = DrConfig.objects.first()
        renterDict = {}
        renterDict['title'] = config.title
        renterDict['vote_intro'] = "      " + config.introduce.replace("<br>","\n").replace("&nbsp"," ")
        renterDict['main_logo'] = "/static/%s" % config.logoimage


        # 查出前6名
        results = (DrVote.objects.order_by('-votecount').all())[:10]
        for index, one in enumerate(results):
            print one.fcode
            factData = DrFactory.objects.filter(code=one.fcode).first()

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