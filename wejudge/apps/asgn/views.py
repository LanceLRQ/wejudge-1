# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.asgn as AsgnKernel


# ======== 作业子系统 ========

def index(request, cid=None):
    viewer = AsgnKernel.AsgnList(request)
    viewer.index(cid)
    return viewer.render()


def score_counter(request, cid):
    viewer = AsgnKernel.AsgnList(request)
    viewer.score_counter(cid)
    return viewer.render()


def problem_list(request, aid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.problem_list(aid)
    return viewer.render()


def asgn_rank_list(request, aid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.asgn_rank_list(aid)
    return viewer.render()


def asgn_answer_view(request, aid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.asgn_answer_view(aid)
    return viewer.render()


def visit_req(request, aid=-1):
    viewer = AsgnKernel.AsgnList(request)
    viewer.visit_req(aid)
    return viewer.render()


def save_visit_req(request, aid=-1):
    viewer = AsgnKernel.AsgnList(request)
    viewer.save_visit_req(aid)
    return viewer.render()


def show_asgn_problem(request, aid=-1, pid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.show_asgn_problem(aid, pid)
    return viewer.render()


def show_my_status_list(request, aid=-1, pid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.my_status_list(aid, pid)
    return viewer.render()


def show_asgn_status_list(request, aid=-1, page=1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.asgn_status_list(aid, int(page))
    return viewer.render()


def show_asgn_report(request, aid=-1, author_id=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.show_report(aid, author_id)
    return viewer.render()


def save_impression(request, aid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.save_impression(aid)
    return viewer.render()


def save_asgn_submission(request, aid=-1, pid=-1):
    viewer = AsgnKernel.AsgnBody(request)
    viewer.save_asgn_submission(aid, pid)
    return viewer.render()

# === mgr ===


def new_asgn(request, cid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.new_asgn(cid)
    return viewer.render()


def save_new_asgn(request, cid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_new_asgn(cid)
    return viewer.render()


def asgn_setting(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_setting(aid)
    return viewer.render()


def save_asgn_setting(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_asgn_setting(aid)
    return viewer.render()


def add_problems(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.add_problems(aid)
    return viewer.render()


def asgn_problem_setting_ajax(request, aid, id):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_problem_setting_ajax(aid, id)
    return viewer.render()


def remove_asgn_problem(request, aid, id):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.remove_asgn_problem(aid, id)
    return viewer.render()


def save_asgn_problem_setting(request, aid, id):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_asgn_problem_setting(aid, id)
    return viewer.render()


def show_asgn_checkup_list(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_checkup_list(aid)
    return viewer.render()


def save_asgn_checkup(request, aid, rid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_asgn_checkup(aid, rid)
    return viewer.render()


def save_asgn_checkup_fast(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_asgn_checkup_fast(aid)
    return viewer.render()


def asgn_arrangement(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_arrangement(aid)
    return viewer.render()


def save_asgn_arrangement(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_asgn_arrangement(aid)
    return viewer.render()


def asgn_mgr_visit_require(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_mgr_visit_require(aid)
    return viewer.render()


def save_mgr_visit_require(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.save_mgr_visit_require(aid)
    return viewer.render()


def mgr_asgn_zip_the_codes(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_zip_the_codes(aid)
    return viewer.render()


def mgr_asgn_zip_code_config(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_zip_code_config(aid)
    return viewer.render()


def mgr_asgn_delete_view(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_delete_view(aid)
    return viewer.render()


def mgr_asgn_delete(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_delete(aid)
    return viewer.render()


# statistics


def mgr_asgn_statistics(request, aid):
    viewer = AsgnKernel.AsgnManager(request)
    viewer.asgn_statistics(aid)
    return viewer.render()


def asgn_statistics_public(request, aid):
    viewer = AsgnKernel.AsgnAnalyzer(request)
    viewer.asgn_public_statistics_analyzer(aid)
    rep = viewer.render()
    rep['Access-Control-Allow-Origin'] = '*'
    return rep


def asgn_score_counter(request, cid):
    viewer = AsgnKernel.AsgnAnalyzer(request)
    viewer.asgn_score_counter(cid)
    rep = viewer.render()
    return rep
