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
    url(r'^$', views.index, name="cpanel_index"),
    url(r'^web_config$', views.web_config, name="cpanel_web_config"),
    url(r'^web_config/save$', views.save_web_config, name="cpanel_save_web_config"),
    url(r'^account/list$', views.accountmgr_view_list, name="cpanel_accountmgr_viewlist"),
    url(r'^account/import$', views.accountmgr_import_account, name="cpanel_accountmgr_import"),
    url(r'^account/import/upload$', views.accountmgr_import_account_upload, name="cpanel_accountmgr_import_upload"),
    url(r'^account/list/page/(?P<page>\d+)$', views.accountmgr_view_list, name="cpanel_accountmgr_viewlist"),
    url(r'^account/list/filter$', views.accountmgr_view_list_filter, name="cpanel_accountmgr_viewlist_filter"),
    url(r'^account/new$', views.accountmgr_new_account, name="cpanel_accountmgr_new_account"),
    url(r'^account/(?P<uid>\w+)/modify$', views.accountmgr_modify_account, name="cpanel_accountmgr_modify_account"),
    url(r'^account/new/save$', views.accountmgr_save_new_account, name="cpanel_accountmgr_save_new_account"),
    url(r'^account/(?P<uid>\w+)/modify/save$', views.accountmgr_save_modify_account, name="cpanel_accountmgr_save_modify_account"),
    url(r'^account/password/reset$', views.accountmgr_reset_password, name="cpanel_accountmgr_reset_password"),
    url(r'^account/delete$', views.accountmgr_delete_account, name="cpanel_accountmgr_delete_account"),
]