#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 数据库模型导入
from time import strftime, localtime
from datetime import timedelta, date
from django.db import transaction
# 公共处理函数
from publicFunction import *

# 公共配置缓存
from HsShareData import *

def getPostData(request):
    postDataList = None
    if request.method == 'POST':
        for key in request.POST:
            postDataList[key] = request.POST.getlist(key)[0]

    import json
    if not postDataList or len(postDataList) == 0:
        try:
            bodyTxt = request.body
            postDataList = json.loads(bodyTxt)
        except Exception,ex:
            pass

    return  postDataList

def get_day_of_day(n=0):
    '''''
    if n>=0,date is larger than today
    if n<0,date is less than today
    date format = "YYYY-MM-DD"
    '''
    if(n<0):
        n = abs(n)
        return date.today()-timedelta(days=n)
    else:
        return date.today()+timedelta(days=n)

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

class PublicService(object):
    #添加用户业务
    @staticmethod
    def validUrl(timesnap,sig):

        result = base64.decodestring(sig)

        try:
            intResult = int(result)

            if intResult == int(timesnap):
                return True
        except:
            return False



        return False


    @staticmethod
    def checkActivitySep(account):
        return False

    @staticmethod
    def checkQuestionSep(account):
        return False


    # 获取图片文件最大索引
    @staticmethod
    def getMaxImageIndex(filePath):
        return  1

    # 检查图片索引是否存在
    @staticmethod
    def checkFileExist(pathDir, index):
        return True

    @staticmethod
    def getAdImageList(adcode):
        currentPath = publicFunction.fetchCurrentPath()
        imagePath = os.path.join(currentPath, "Attach")
        imagePath = os.path.join(imagePath, "Ad")
        imagePath = os.path.join(imagePath, adcode)

        if not os.path.isdir(imagePath):
            return []

        # 如果目录已经存在
        Files = []
        for root, dirs, files in os.walk(imagePath):
            for fn in files:
                try:
                    # fileTemp = os.path.join(root,fn)
                    shotname, extension = os.path.splitext(fn)
                    # temps = shotname.split('_')
                    Files.append(fn)
                except:
                    continue


        Files.sort(reverse=False)

        return Files

    @staticmethod
    def removeResource(code,orgcode,filename = None, Type = 0):
        currentPath = publicFunction.fetchCurrentPath()
        imagePath = os.path.join(currentPath, "Attach")
        imagePath = os.path.join(imagePath, orgcode)
        if Type == 0:
            imagePath = os.path.join(imagePath, "Product")
        elif Type == 1:
            imagePath = os.path.join(imagePath, "Service")
        elif Type == 12:
            imagePath = os.path.join(imagePath, "Activity")
        elif Type == 13:
            imagePath = os.path.join(imagePath, "Shop")
        elif Type == 14:
            imagePath = os.path.join(imagePath, "Advertise")

        imagePath = os.path.join(imagePath, code)

        if not filename:
            import  shutil
            shutil.rmtree(imagePath,True)
        else:
            fileFullName = os.path.join(imagePath,filename)
            try:
                os.remove(fileFullName)
            except:
                pass

    @staticmethod
    def saveResource(orgcode,adcode,imagedata,filename):
        currentPath = publicFunction.fetchCurrentPath()
        imagePath = os.path.join(currentPath,"Attach")
        imagePath = os.path.join(imagePath,orgcode)
        imagePath = os.path.join(imagePath,adcode)

        if not os.path.isdir(imagePath):
            os.makedirs(imagePath)

        filename = os.path.join(imagePath,filename)

        index = 1
        while os.path.isfile(filename):
            filename = os.path.join(imagePath,"%d_%s"%(index ,filename))
            index = index + 1

        file = open(filename, "wb")
        file.write(imagedata)
        file.close()
        return

    # @staticmethod
    # def getLastedVersion(terminal):
    #     try:
    #         newVersionHandle = MrmfVersion.objects.get(stype=terminal)
    #     except Exception,ex:
    #         pass
    #
    #     rtnVersion = {}
    #     rtnVersion["VersionCode"] = newVersionHandle.value
    #     rtnVersion["Url"] = newVersionHandle.url
    #
    #     return  rtnVersion

