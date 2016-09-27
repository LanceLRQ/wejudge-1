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
    3. Add a URL to urlpatterns:  url(r'^blog/s', include(blog_urls))
"""

import views
from django.conf.urls import url

urlpatterns = [
    # url(r'^login$', views.login, name="account_login"),
    # url(r'^register$', views.register, name="account_register"),
    url(r'^rank$', views.RankList, name="account_ranklist"),
    url(r'^rank/(?P<page>\d+)$', views.RankList, name="account_ranklist"),
    url(r'^register/save$', views.save_register, name="account_save_register"),
    url(r'^register/student/vaild$', views.save_register_student, name="account_save_register_student"),
    url(r'^logout$', views.logout, name="account_logout"),
    url(r'^login/ajax$', views.login_ajax, name="account_login_ajax"),
    url(r'^api/check_login$', views.api_check_login, name="account_api_check_login"),
    url(r'^findpwd$', views.find_pwd_start, name="account_find_pwd_start"),
    url(r'^findpwd/valid$', views.find_pwd_final, name="account_find_pwd_final"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/$', views.space, name="account_space"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/detail$', views.user_detail, name="account_user_detail"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/email$', views.email_vaild, name="account_email_vaild"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/email/valid$', views.email_vaild_check, name="account_email_vaild_check"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/modify$', views.user_modify, name="account_user_modify"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/modify/save$', views.save_user_modify, name="account_save_user_modify"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/avatar$', views.user_avatar, name="account_user_avatar"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/avatar/save$', views.save_user_avatar, name="account_save_user_avatar"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/wechat$', views.user_wechat, name="account_user_wechat"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/wechat/unbind$', views.user_wechat_unbind, name="account_user_wechat_unbind"),
    url(r'^(?P<uid>[0-9A-z_]+)/space/wechat/refresh_headimg$', views.user_wechat_refresh_headimg, name="account_user_wechat_refresh_headimg"),
    url(r'^space/me/preference/problem_detail_list/(?P<mode>[0-1]+)$', views.change_preference_problem_detail_list, name="account_change_preference_problem_detail_list"),
]
