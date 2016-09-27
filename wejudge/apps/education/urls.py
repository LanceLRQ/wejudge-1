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
    url(r'^$', views.index, name="education_index"),
    url(r'^course/(?P<cid>\d+)$', views.index, name="education_index"),
    url(r'^course/(?P<cid>\d+)/info$', views.course_info, name="education_course_info"),
    url(r'^course/(?P<cid>\d+)/message$', views.course_message, name="education_course_message"),
    url(r'^course/choosing$', views.course_choosing, name="education_course_choosing"),
    url(r'^course/choosing/save$', views.save_course_choosing, name="education_save_course_choosing"),
    url(r'^course/(?P<cid>\d+)/choosing$', views.course_choosing, name="education_course_choosing"),
    url(r'^course/(?P<cid>\d+)/message/(?P<mid>\d+)$', views.course_message_detail, name="education_course_message_detail"),
    url(r'^course/(?P<cid>\d+)/repositories$', views.resource_repositories, name="education_resource_repositories"),
    url(r'^course/(?P<cid>\d+)/arrangement/(?P<aid>\d+)/remove$', views.remove_arrangement, name="education_remove_arrangement"),

    url(r'^repository$', views.repository_index, name="education_repository_index"),
    url(r'^repository/(?P<handle>\w+)$', views.repository_index, name="education_repository_index"),
    url(r'^repository/new/save$', views.change_repository, name="education_save_new_repository"),
    url(r'^repository/(?P<handle>\w+)/delete$', views.delete_repository, name="education_delete_repository"),
    url(r'^repository/(?P<handle>\w+)/modify/save$', views.change_repository, name="education_save_modify_repository"),
    url(r'^repository/(?P<handle>\w+)/content/delete$', views.repository_delete_files, name="education_repository_delete_files"),
    url(r'^repository/(?P<handle>\w+)/upload$', views.repository_upload_file, name="education_repository_upload_file"),
    url(r'^repository/(?P<handle>\w+)/folder/new$', views.repository_new_folder, name="education_repository_new_folder"),

    url(r'^course/new$', views.new_course, name="education_mgr_new_course"),
    url(r'^course/new/save$', views.save_new_course, name="education_mgr_save_new_course"),
    url(r'^course/(?P<cid>\d+)/modify$', views.modify_course, name="education_mgr_modify_course"),
    url(r'^course/(?P<cid>\d+)/modify/save$', views.save_modify_course, name="education_mgr_save_modify_course"),
    url(r'^course/(?P<cid>\d+)/delete$', views.delete_course, name="education_mgr_delete_course"),
    url(r'^course/(?P<cid>\d+)/mgr/message/new$', views.new_course_message, name="education_mgr_new_course_message"),
    url(r'^course/(?P<cid>\d+)/mgr/message/new/save$', views.save_new_course_message, name="education_mgr_save_new_course_message"),
    url(r'^course/(?P<cid>\d+)/mgr/message/(?P<mid>\d+)/modify$', views.modify_course_message, name="education_mgr_modify_course_message"),
    url(r'^course/(?P<cid>\d+)/mgr/message/(?P<mid>\d+)/save$', views.save_modify_course_message, name="education_mgr_save_modify_course_message"),
    url(r'^course/(?P<cid>\d+)/mgr/message/(?P<mid>\d+)/delete$', views.delete_course_message, name="education_mgr_delete_course_message"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement$', views.course_arrangement, name="education_mgr_course_arrangement"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement/new$', views.new_course_arrangement, name="education_mgr_new_course_arrangement"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement/new/save$', views.save_new_course_arrangement, name="education_mgr_save_new_course_arrangement"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement/(?P<aid>\d+)/modify$', views.modify_course_arrangement, name="education_mgr_modify_course_arrangement"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement/(?P<aid>\d+)/save$', views.save_modify_course_arrangement, name="education_mgr_save_modify_course_arrangement"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement/(?P<aid>\d+)/delete$', views.delete_course_arrangement, name="education_mgr_delete_course_arrangement"),
    url(r'^course/(?P<cid>\d+)/mgr/arrangement/(?P<aid>\d+)/signature', views.get_arrangement_signature, name="education_mgr_get_arrangement_signature"),
    url(r'^course/(?P<cid>\d+)/mgr/students$', views.course_student, name="education_mgr_course_student"),
    url(r'^course/(?P<cid>\d+)/mgr/students/change$', views.change_course_students, name="education_mgr_change_course_students"),
    url(r'^course/(?P<cid>\d+)/mgr/students/add$', views.add_course_students, name="education_mgr_add_course_students"),
    url(r'^course/(?P<cid>\d+)/mgr/assistants$', views.course_assistants, name="education_mgr_course_assistants"),
    url(r'^course/(?P<cid>\d+)/mgr/assistants/add$', views.add_course_assistants, name="education_mgr_add_course_assistants"),
    url(r'^course/(?P<cid>\d+)/mgr/assistants/change$', views.change_course_assistants, name="education_mgr_change_course_assistants"),
    url(r'^course/(?P<cid>\d+)/mgr/resource/repositories/enable$', views.enable_resource_repositories, name="education_mgr_enable_resource_repositories"),

]
