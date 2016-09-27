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
    url(r'^$', views.index, name="asgn_index"),
    url(r'^course/(?P<cid>\d+)$', views.index, name="asgn_index"),
    url(r'^course/(?P<cid>\d+)/counter$', views.score_counter, name="asgn_score_counter"),
    url(r'^course/(?P<cid>\d+)/counter/result$', views.asgn_score_counter, name="asgn_score_counter_result"),

    url(r'^(?P<aid>\d+)$', views.problem_list, name="asgn_problem_list"),
    url(r'^(?P<aid>\d+)/visit_req$', views.visit_req, name="asgn_visit_req"),
    url(r'^(?P<aid>\d+)/visit_req/save$', views.save_visit_req, name="asgn_save_visit_req"),
    url(r'^(?P<aid>\d+)/status$', views.show_asgn_status_list, name="asgn_status_list"),
    url(r'^(?P<aid>\d+)/status/page/(?P<page>\d+)$', views.show_asgn_status_list, name="asgn_status_list"),
    url(r'^(?P<aid>\d+)/rank_list$', views.asgn_rank_list, name="asgn_rank_list"),
    url(r'^(?P<aid>\d+)/answer$', views.asgn_answer_view, name="asgn_answer_view"),
    url(r'^(?P<aid>\d+)/problem/(?P<pid>\d+)$', views.show_asgn_problem, name="asgn_show_asgn_problem"),
    url(r'^(?P<aid>\d+)/problem/(?P<pid>\d+)/my_status_list$', views.show_my_status_list, name="asgn_show_my_status_list"),
    url(r'^(?P<aid>\d+)/problem/(?P<pid>\d+)/submit$', views.save_asgn_submission, name="asgn_save_submission"),
    url(r'^(?P<aid>\d+)/report/(?P<author_id>\w+)$', views.show_asgn_report, name="asgn_show_report"),
    url(r'^(?P<aid>\d+)/report/save/impression$', views.save_impression, name="asgn_save_impression"),



    url(r'^mgr/course/(?P<cid>\d+)/new_asgn$', views.new_asgn, name="asgn_mgr_new_asgn"),
    url(r'^mgr/course/(?P<cid>\d+)/new_asgn/save$', views.save_new_asgn, name="asgn_mgr_save_new_asgn"),
    url(r'^(?P<aid>\d+)/mgr/setting$', views.asgn_setting, name="asgn_mgr_asgn_setting"),
    url(r'^(?P<aid>\d+)/mgr/setting/save$', views.save_asgn_setting, name="asgn_mgr_save_asgn_setting"),
    url(r'^(?P<aid>\d+)/mgr/add/problems$', views.add_problems, name="asgn_mgr_add_problems"),
    url(r'^(?P<aid>\d+)/mgr/checkup/list$', views.show_asgn_checkup_list, name="asgn_mgr_show_asgn_checkup_list"),
    url(r'^(?P<aid>\d+)/mgr/checkup/(?P<rid>\d+)/save$', views.save_asgn_checkup, name="asgn_mgr_save_asgn_checkup"),
    url(r'^(?P<aid>\d+)/mgr/checkup/fast/save$', views.save_asgn_checkup_fast, name="asgn_mgr_save_asgn_checkup_fast"),
    url(r'^(?P<aid>\d+)/mgr/ap_setting/byid/(?P<id>\d+)$', views.asgn_problem_setting_ajax, name="asgn_mgr_asgn_problem_setting_ajax"),
    url(r'^(?P<aid>\d+)/mgr/ap_setting/byid/(?P<id>\d+)/save$', views.save_asgn_problem_setting, name="asgn_mgr_save_asgn_problem_setting"),
    url(r'^(?P<aid>\d+)/mgr/ap_setting/byid/(?P<id>\d+)/remove', views.remove_asgn_problem, name="asgn_mgr_remove_asgn_problem"),
    url(r'^(?P<aid>\d+)/mgr/arrangement$', views.asgn_arrangement, name="asgn_mgr_asgn_arrangement"),
    url(r'^(?P<aid>\d+)/mgr/arrangement/save$', views.save_asgn_arrangement, name="asgn_mgr_save_asgn_arrangement"),
    url(r'^(?P<aid>\d+)/mgr/visit_require$', views.asgn_mgr_visit_require, name="asgn_mgr_asgn_visit_require"),
    url(r'^(?P<aid>\d+)/mgr/visit_require/save$', views.save_mgr_visit_require, name="asgn_mgr_save_mgr_visit_require"),
    url(r'^(?P<aid>\d+)/mgr/zip_code$', views.mgr_asgn_zip_the_codes, name="asgn_mgr_zip_the_codes"),
    url(r'^(?P<aid>\d+)/mgr/zip_code/config$', views.mgr_asgn_zip_code_config, name="asgn_mgr_zip_code_config"),
    url(r'^(?P<aid>\d+)/mgr/statistics$', views.mgr_asgn_statistics, name="asgn_statistics"),
    url(r'^(?P<aid>\d+)/mgr/delete$', views.mgr_asgn_delete_view, name="asgn_mgr_delete_view"),
    url(r'^(?P<aid>\d+)/mgr/delete/do$', views.mgr_asgn_delete, name="mgr_asgn_delete"),
    url(r'^(?P<aid>\d+)/statistics/api/public$', views.asgn_statistics_public, name="asgn_statistics_public"),


]
