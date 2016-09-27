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
    url(r'^archive$', views.archive, name="problem_archive"),
    url(r'^archive/page/(?P<page>\d+)$', views.archive, name="problem_archive"),
    url(r'^archive/filter$$', views.archive_get_filter_page, name="problem_archive_get_filter_page"),

    url(r'^judge/status/(?P<sid>\d+)$', views.judge_detail, name="problem_judge_detail"),
    url(r'^judge/status/(?P<sid>\d+)/json$', views.get_judge_status, name="api_get_judge_status"),
    url(r'^judge/status/filter$', views.judge_status_get_filter_page, name="problem_judge_status_get_filter_page"),
    url(r'^judge/status/list$', views.show_judge_status_list, name="problem_judge_status"),
    url(r'^judge/status/list/page/(?P<page>\d+)$', views.show_judge_status_list, name="problem_judge_status"),
    url(r'^judge/status/in_problem/(?P<pid>\d+)$', views.status_list_in_problem, name="problem_judge_status_in_problem"),

    url(r'^judge/api/receive_judge_result/(?P<sid>\d+)$', views.api_receive_judge_result),
    url(r'^judge/api/get_problem_judge_options/(?P<sid>\d+)$', views.api_get_problem_judge_options),
    url(r'^tdmaker/api/get_problem_judge_options/(?P<id>\d+)$', views.tdmaker_get_problem_judge_options),
    url(r'^tdmaker/api/receive_judge_result/(?P<id>\d+)$', views.tdmaker_receive_judge_result),

    url(r'^(?P<pid>\d+)$', views.show_problem, name="problem_show"),
    url(r'^(?P<pid>\d+)/submit$', views.save_submission, name="problem_submit"),
    url(r'^(?P<pid>\d+)/judge_history', views.get_judge_history, name="problem_judge_history"),

    url(r'^classify/list.json$', views.get_classify_list, name="problem_get_classify_list"),
    url(r'^classify/selector$', views.classify_selector, name="problem_classify_selector"),
    url(r'^classify/(?P<now_id>\d+)/list.json$', views.get_classify_list, name="problem_get_classify_list"),
    url(r'^classify/(?P<id>\d+)/new$', views.new_classify, name="problem_new_classify"),
    url(r'^classify/(?P<id>\d+)/new/save$', views.save_new_classify, name="problem_save_new_classify"),
    url(r'^classify/(?P<id>\d+)/modify$', views.modify_classify, name="problem_modify_classify"),
    url(r'^classify/(?P<id>\d+)/modify/save$', views.save_modify_classify, name="problem_save_modify_classify"),
    url(r'^classify/(?P<id>\d+)/delete$', views.delete_classify, name="problem_delete_classify"),


    url(r'^mgr/batch_change_visiable/(?P<flag>\d+)$', views.mgr_batch_change_visiable, name="problem_mgr_batch_change_visiable"),
    url(r'^mgr/save_classify_to_problem/(?P<cid>\d+)$', views.mgr_save_classify_to_problem, name="problem_mgr_save_classify_to_problem"),
    url(r'^mgr/problem/new$', views.mgr_new_problem, name="problem_mgr_new_problem"),
    url(r'^mgr/problem/new/save$', views.mgr_save_new_problem, name="problem_mgr_save_new_problem"),
    url(r'^mgr/problem/(?P<pid>\d+)$', views.mgr_modify_problem, name="problem_mgr_modify_problem"),
    url(r'^mgr/problem/(?P<pid>\d+)/delete$', views.mgr_delete_problem, name="problem_mgr_delete_problem"),
    url(r'^mgr/problem/(?P<pid>\d+)/pause_judge/(?P<pause>[01])$', views.mgr_change_problem_judge_pause, name="problem_mgr_change_problem_judge_pause"),
    url(r'^mgr/problem/(?P<pid>\d+)/infomation/save$', views.mgr_save_problem_infomation, name="problem_mgr_save_problem_info"),
    url(r'^mgr/problem/(?P<pid>\d+)/demo_code/save$', views.mgr_save_demo_code, name="problem_mgr_save_demo_code"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/(?P<handle>\w+)/setting$', views.mgr_testdata_setting, name="problem_mgr_testdata_setting"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/(?P<handle>\w+)/view$', views.mgr_testdata_view, name="problem_mgr_testdata_view"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/(?P<handle>\w+)/download/(?P<ftype>in|out)$', views.mgr_testdata_download, name="problem_mgr_testdata_download"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/(?P<handle>\w+)/delete$', views.mgr_delete_testdata, name="problem_mgr_delete_testdata"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/(?P<handle>\w+)/upload$', views.mgr_upload_testdata, name="problem_mgr_upload_testdata"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/(?P<handle>\w+)/upload/save$', views.mgr_upload_testdata_api, name="problem_mgr_upload_testdata_api"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/setting/save$', views.mgr_save_testdata_setting, name="problem_mgr_save_testdata_setting"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/view/save$', views.mgr_save_testdata_view, name="problem_mgr_save_testdata_view"),
    url(r'^mgr/problem/(?P<pid>\d+)/test_data/new$', views.mgr_new_testdata, name="problem_mgr_new_testdata"),
    url(r'^mgr/problem/(?P<pid>\d+)/tdmaker/add_queue$', views.mgr_run_tdmaker, name="problem_mgr_run_tdmaker"),
]
