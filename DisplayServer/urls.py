#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""DisplayServer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from DSServer.Api.WebCenterApi import *

urlpatterns = [
    # API接口
    url(r'^admin/', admin.site.urls),
    url(r'^$',WebCenterApi.goHome),
    url(r'^api/vote/$', WebCenterApi.CommandDispatch),
    url(r'^vote_introduce.html',WebCenterApi.openIntroduce),
    url(r'^vote_expert.html',WebCenterApi.openExpet),
    url(r'^vote_number.html',WebCenterApi.openVoteNumber),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)