"""wejudge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

import views
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^$', views.index, name="wejuge_index"),
    url(r'^api/ckeditor/imgupload$', views.ckeditor_imgupload),
    url(r'^wechat/api/oauth2/callback$', views.wcapi_oauth2callback),
    # url(r'^gen_pwd$', views.gen_pwd),
    # url(r'^fix_asgn_report$', views.fix_asgn_report),
    # url(r'^create_contest_account$', views.create_contest_account),
    # url(r'^refresh_account_sex$', views.refresh_account_sex),
    # url(r'^refresh_account_realname$', views.refresh_account_realname),
]
