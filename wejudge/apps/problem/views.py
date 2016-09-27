# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.problem as ProblemKernel


# ======== 题库子系统 ========

# 题库首页
def archive(request, page=1):
    viewer = ProblemKernel.ProblemArchive(request)
    viewer.list_archive(int(page))
    return viewer.render()


# 题库过滤器页面
def archive_get_filter_page(request):
    viewer = ProblemKernel.ProblemArchive(request)
    viewer.get_filter_page()
    return viewer.render()


# 展示问题
def show_problem(request, pid):
    viewer = ProblemKernel.ProblemBody(request)
    viewer.show_problem(pid)
    return viewer.render()


# 问题提交接口
def save_submission(request, pid):
    viewer = ProblemKernel.ProblemBody(request)
    viewer.save_submission(pid)
    return viewer.render()


# 获取问题评测历史接口
def get_judge_history(request, pid):
    viewer = ProblemKernel.ProblemBody(request)
    viewer.get_judge_history(pid)
    return viewer.render()

# ======== 题目管理接口 ========


def mgr_batch_change_visiable(request, flag):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.batch_change_visiable(flag)
    return viewer.render()


def mgr_new_problem(request):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.new_problem()
    return viewer.render()


def mgr_save_new_problem(request):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.save_new_problem()
    return viewer.render()


def mgr_modify_problem(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.modify_problem(pid)
    return viewer.render()


def mgr_change_problem_judge_pause(request, pid, pause):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.change_problem_judge_pause(pid, pause)
    return viewer.render()


def mgr_delete_problem(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.delete_problem(pid)
    return viewer.render()


def mgr_save_problem_infomation(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.save_problem_infomation(pid)
    return viewer.render()


def mgr_save_demo_code(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.save_problem_demo_code(pid)
    return viewer.render()


def mgr_testdata_view(request, pid, handle):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.testdata_view(pid, handle)
    return viewer.render()


def mgr_testdata_setting(request, pid, handle):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.testdata_setting(pid, handle)
    return viewer.render()


def mgr_save_testdata_setting(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.save_testdata_setting(pid)
    return viewer.render()


def mgr_delete_testdata(request, pid, handle):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.delete_testdata(pid, handle)
    return viewer.render()


def mgr_testdata_download(request, pid, handle, ftype):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.testdata_download(pid, handle, ftype)
    return viewer.render()


def mgr_new_testdata(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.new_testdata(pid)
    return viewer.render()


def mgr_upload_testdata(request, pid, handle):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.testdata_upload(pid, handle)
    return viewer.render()


def mgr_upload_testdata_api(request, pid, handle):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.testdata_upload_api(pid, handle)
    return viewer.render()


def mgr_save_testdata_view(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.save_testdata_view(pid)
    return viewer.render()


def mgr_run_tdmaker(request, pid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.run_tdmaker(pid)
    return viewer.render()


def mgr_save_classify_to_problem(request, cid):

    viewer = ProblemKernel.ProblemManager(request)
    viewer.save_classify_to_problem(cid)
    return viewer.render()



# ======== 评测状态子系统 ========

# 评测状态列表
def show_judge_status_list(request, page=1):
    viewer = ProblemKernel.JudgeStatus(request)
    viewer.status_list(int(page))
    return viewer.render()


# 评测状态列表(问题详情内）
def status_list_in_problem(request, pid):
    viewer = ProblemKernel.JudgeStatus(request)
    viewer.status_list_in_problem(pid)
    return viewer.render()


# 评测状态列表(问题详情内）
def judge_detail(request, sid):
    viewer = ProblemKernel.JudgeStatus(request)
    viewer.judge_detail(sid)
    return viewer.render()


# 评测状态过滤器页面
def judge_status_get_filter_page(request):
    viewer = ProblemKernel.JudgeStatus(request)
    viewer.get_filter_page()
    return viewer.render()


# ======== 问题分类子系统 ========

def get_classify_list(request, now_id=None):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.get_classify_list(now_id)
    rend = viewer.render()
    rend['Content-Type']= "application/json"
    return rend


def new_classify(request, id=None):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.classify_editor(id, True)
    return viewer.render()


def modify_classify(request, id=None):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.classify_editor(id, False)
    return viewer.render()


def save_new_classify(request, id=None):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.save_classify_editor(id, True)
    return viewer.render()


def save_modify_classify(request, id=None):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.save_classify_editor(id, False)
    return viewer.render()


def delete_classify(request, id):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.delete_classify(id)
    return viewer.render()


def classify_selector(request):
    viewer = ProblemKernel.ProblemClassify(request)
    viewer.classify_selector()
    return viewer.render()


# ======== 评测机通信接口 ========

# 评测机接口：获取问题评测信息
def api_get_problem_judge_options(request, sid):
    viewr = ProblemKernel.JudgeServiceAPI(request)
    viewr.get_problem_judge_options(sid)
    return viewr.render()


# 评测机接口：接受评测结果
def api_receive_judge_result(request, sid):
    viewr = ProblemKernel.JudgeServiceAPI(request)
    viewr.receive_judge_result(sid)
    return viewr.render()


# 评测机接口【TDMaker】：获取问题评测信息
def tdmaker_get_problem_judge_options(request, id):
    viewr = ProblemKernel.JudgeServiceAPI(request)
    viewr.tdmaker_get_problem_judge_options(id)
    return viewr.render()


# 评测机接口【TDMaker】：接受评测结果
def tdmaker_receive_judge_result(request, id):
    viewr = ProblemKernel.JudgeServiceAPI(request)
    viewr.tdmaker_receive_judge_result(id)
    return viewr.render()


# 评测机状态接口：读取当前评测状态
def get_judge_status(request, sid):
    viewr = ProblemKernel.JudgeServiceAPI(request)
    viewr.get_judge_status(sid)
    return viewr.render()

