# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.education as EduKernel


# ======== 教学中心子系统 ========

def index(request, cid=None):
    # 教学中心首页
    viewer = EduKernel.EducationCenter(request)
    viewer.index(cid)
    return viewer.render()


def course_info(request, cid):
    # 课程信息
    viewer = EduKernel.EducationCenter(request)
    viewer.course_info(cid)
    return viewer.render()


def course_message(request, cid):
    # 课程通知
    viewer = EduKernel.EducationCenter(request)
    viewer.course_message(cid)
    return viewer.render()


def course_message_detail(request, cid, mid):
    # 课程通知详情
    viewer = EduKernel.EducationCenter(request)
    viewer.course_message_detail(cid, mid)
    return viewer.render()


def course_choosing(request, cid=None):
    # 学生选课
    viewer = EduKernel.EducationCenter(request)
    viewer.course_choosing(cid)
    return viewer.render()


def save_course_choosing(request):
    # 保存学生选课
    viewer = EduKernel.EducationCenter(request)
    viewer.save_course_choosing()
    return viewer.render()


def remove_arrangement(request, cid, aid):
    # 退选课程
    viewer = EduKernel.EducationCenter(request)
    viewer.remove_arrangement(cid, aid)
    return viewer.render()


def resource_repositories(request, cid):
    # 教学资料库
    viewer = EduKernel.EducationCenter(request)
    viewer.resource_repositories(cid)
    return viewer.render()



# === MGR ===


def new_course(request):
    # 新建课程(AJAX)
    viewer = EduKernel.EducationManager(request)
    viewer.course_editor()
    return viewer.render()


def modify_course(request, cid):
    # 新建课程(AJAX)
    viewer = EduKernel.EducationManager(request)
    viewer.course_editor(cid)
    return viewer.render()


def save_new_course(request):
    # 保存新建课程(JSON)
    viewer = EduKernel.EducationManager(request)
    viewer.save_course_editor()
    return viewer.render()


def save_modify_course(request, cid):
    # 保存新建课程(JSON)
    viewer = EduKernel.EducationManager(request)
    viewer.save_course_editor(cid)
    return viewer.render()


def delete_course(request, cid):
    # 删除课程(JSON)
    viewer = EduKernel.EducationManager(request)
    viewer.course_delete(cid)
    return viewer.render()


def new_course_message(request, cid):
    # 课程通知
    viewer = EduKernel.EducationManager(request)
    viewer.new_course_message(cid)
    return viewer.render()


def save_new_course_message(request, cid):
    # 课程通知
    viewer = EduKernel.EducationManager(request)
    viewer.save_new_course_message(cid)
    return viewer.render()


def modify_course_message(request, cid, mid):
    # 课程通知
    viewer = EduKernel.EducationManager(request)
    viewer.modify_course_message(cid, mid)
    return viewer.render()


def save_modify_course_message(request, cid, mid):
    # 课程通知
    viewer = EduKernel.EducationManager(request)
    viewer.save_modify_course_message(cid, mid)
    return viewer.render()


def delete_course_message(request, cid, mid):
    # 删除课程通知
    viewer = EduKernel.EducationManager(request)
    viewer.delete_course_message(cid, mid)
    return viewer.render()


def course_arrangement(request, cid):
    # 排课管理
    viewer = EduKernel.EducationManager(request)
    viewer.course_arrangement(cid)
    return viewer.render()


def get_arrangement_signature(request, cid, aid):
    # 排课管理-获取选课授权码
    viewer = EduKernel.EducationManager(request)
    viewer.get_arrangement_signature(cid, aid)
    return viewer.render()


def modify_course_arrangement(request, cid, aid):
    # 排课管理-编辑排课信息
    viewer = EduKernel.EducationManager(request)
    viewer.modify_course_arrangement(cid, aid)
    return viewer.render()


def save_modify_course_arrangement(request, cid, aid):
    # 排课管理-保存编辑排课信息
    viewer = EduKernel.EducationManager(request)
    viewer.save_modify_course_arrangement(cid, aid)
    return viewer.render()


def new_course_arrangement(request, cid):
    # 排课管理-新建排课信息
    viewer = EduKernel.EducationManager(request)
    viewer.new_course_arrangement(cid)
    return viewer.render()


def save_new_course_arrangement(request, cid):
    # 排课管理-保存新建排课信息
    viewer = EduKernel.EducationManager(request)
    viewer.save_new_course_arrangement(cid)
    return viewer.render()


def delete_course_arrangement(request, cid, aid):
    # 排课管理-删除排课信息
    viewer = EduKernel.EducationManager(request)
    viewer.delete_course_arrangement(cid, aid)
    return viewer.render()


def course_student(request, cid):
    # 学生管理
    viewer = EduKernel.EducationManager(request)
    viewer.course_student(cid)
    return viewer.render()


def change_course_students(request, cid):
    # 学生管理-更改排课信息
    viewer = EduKernel.EducationManager(request)
    viewer.change_course_students(cid)
    return viewer.render()


def add_course_students(request, cid):
    # 学生管理-添加学生
    viewer = EduKernel.EducationManager(request)
    viewer.add_course_students(cid)
    return viewer.render()


def course_assistants(request, cid):
    # 助教管理
    viewer = EduKernel.EducationManager(request)
    viewer.course_assistants(cid)
    return viewer.render()


def add_course_assistants(request, cid):
    # 助教管理：添加助教
    viewer = EduKernel.EducationManager(request)
    viewer.add_course_assistants(cid)
    return viewer.render()


def change_course_assistants(request, cid):
    # 助教管理：助教信息更改
    viewer = EduKernel.EducationManager(request)
    viewer.change_course_assistants(cid)
    return viewer.render()


def enable_resource_repositories(request, cid):
    # 教学资料：启用仓库
    viewer = EduKernel.EducationManager(request)
    viewer.enable_resource_repositories(cid)
    return viewer.render()

# === 仓库 ===


def repository_index(request, handle=None):
    # 仓库主页
    viewer = EduKernel.EducationRepositories(request)
    viewer.repository_index(handle)
    return viewer.render()


def change_repository(request, handle=None):
    # 更改仓库信息：新建、修改
    viewer = EduKernel.EducationRepositories(request)
    viewer.change_repository(handle)
    return viewer.render()

def delete_repository(request, handle=None):
    # 删除仓库
    viewer = EduKernel.EducationRepositories(request)
    viewer.delete_repository(handle)
    return viewer.render()


def repository_delete_files(request, handle=None):
    # 仓库操作：删除文件、文件夹
    viewer = EduKernel.EducationRepositories(request)
    viewer.repository_delete_files(handle)
    return viewer.render()


def repository_upload_file(request, handle=None):
    # 仓库操作：上传文件
    viewer = EduKernel.EducationRepositories(request)
    viewer.repository_upload_file(handle)
    return viewer.render()


def repository_new_folder(request, handle=None):
    # 仓库操作：新建文件夹
    viewer = EduKernel.EducationRepositories(request)
    viewer.repository_new_folder(handle)
    return viewer.render()


