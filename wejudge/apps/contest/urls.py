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

urlpatterns = [
    url(r'^$', views.index, name="contest_index"),
    url(r'^list/page/(?P<page>\d+)$', views.list, name="contest_list"),
    url(r'^new$', views.new_contest, name="new_contest"),
    url(r'^new/save$', views.save_new_contest, name="save_new_contest"),
    url(r'^(?P<cid>\d+)$', views.contest_body, name="contest_body"),
    url(r'^(?P<cid>\d+)/problem/list$', views.problems_list, name="contest_problems_list"),
    url(r'^(?P<cid>\d+)/problem/(?P<pid>\d+)$', views.show_problem, name="contest_show_problem"),
    url(r'^(?P<cid>\d+)/problem/(?P<pid>\d+)/submit$', views.contest_submit_code, name="contest_submit_code"),
    url(r'^(?P<cid>\d+)/status$', views.contest_status, name="contest_status"),
    url(r'^(?P<cid>\d+)/status/page/(?P<page>\d+)$', views.contest_status, name="contest_status"),
    url(r'^(?P<cid>\d+)/rank_list$', views.contest_rank_list, name="contest_rank_list"),
    url(r'^(?P<cid>\d+)/faq$', views.contest_faq, name="contest_faq"),
    url(r'^(?P<cid>\d+)/faq/new$', views.contest_faq_new_msg, name="contest_faq_new_msg"),
    url(r'^(?P<cid>\d+)/faq/new/save$', views.contest_faq_save_new_msg, name="contest_faq_save_new_msg"),
    url(r'^(?P<cid>\d+)/faq/del$', views.contest_faq_del, name="contest_faq_del"),
    url(r'^(?P<cid>\d+)/faq/reply/(?P<fid>\d+)$', views.contest_faq_reply_msg, name="contest_faq_reply_msg"),
    url(r'^(?P<cid>\d+)/faq/reply/(?P<fid>\d+)/save$', views.contest_faq_save_reply, name="contest_faq_save_reply"),

    url(r'^(?P<cid>\d+)/mgr/setting$', views.contest_mgr_contest_setting, name="contest_mgr_contest_setting"),
    url(r'^(?P<cid>\d+)/mgr/setting/save$', views.contest_mgr_save_contest_setting, name="contest_mgr_save_contest_setting"),
    url(r'^(?P<cid>\d+)/mgr/user$', views.contest_mgr_user, name="contest_mgr_user"),
    url(r'^(?P<cid>\d+)/mgr/user/read_xls$', views.contest_mgr_read_xls_to_change_team_user_info, name="contest_mgr_read_xls_to_change_team_user_info"),
    url(r'^(?P<cid>\d+)/mgr/user/reset_pwd$', views.contest_mgr_reset_user_passwd, name="contest_mgr_reset_user_passwd"),
    url(r'^(?P<cid>\d+)/mgr/user/lock_or_unlock$', views.contest_mgr_lock_contest_user, name="contest_mgr_lock_contest_user"),
    url(r'^(?P<cid>\d+)/mgr/add_new_problems$', views.contest_mgr_add_new_problems, name="contest_mgr_add_new_problems"),
    url(r'^(?P<cid>\d+)/mgr/remove_problems$', views.contest_mgr_remove_problems, name="contest_mgr_remove_problems"),
    url(r'^(?P<cid>\d+)/mgr/problem/(?P<pid>\d+)/setting$', views.contest_mgr_problem_setting, name="contest_mgr_problem_setting"),
    url(r'^(?P<cid>\d+)/mgr/problem/(?P<pid>\d+)/setting/save$', views.contest_mgr_save_problem_setting, name="contest_mgr_save_problem_setting"),
    url(r'^(?P<cid>\d+)/mgr/problem/(?P<pid>\d+)/rejudge$', views.contest_mgr_start_problem_rejudge, name="contest_mgr_start_problem_rejudge"),
    url(r'^(?P<cid>\d+)/mgr/status/(?P<sid>\d+)/change$', views.contest_mgr_change_status, name="contest_mgr_change_status"),
    url(r'^(?P<cid>\d+)/mgr/status/(?P<sid>\d+)/change$', views.contest_mgr_change_status, name="contest_mgr_change_status"),
    url(r'^(?P<cid>\d+)/mgr/code_analyzer$', views.contest_mgr_code_analyzer, name="contest_mgr_code_analyzer"),
    url(r'^(?P<cid>\d+)/mgr/code_analyzer/page/(?P<page>\d+)$', views.contest_mgr_code_analyzer, name="contest_mgr_code_analyzer"),
    url(r'^(?P<cid>\d+)/mgr/code_compare/(?P<caid>\d+)$', views.contest_mgr_code_compare, name="contest_mgr_code_compare"),
]