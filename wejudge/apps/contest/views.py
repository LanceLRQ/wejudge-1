from django.shortcuts import render
import wejudge.kernel.contest as ContestKernel
# Create your views here.


def index(request):
    viewer = ContestKernel.ContestList(request)
    viewer.contest_index()
    return viewer.render()


def list(request, page=1):
    viewer = ContestKernel.ContestList(request)
    viewer.contest_list(int(page))
    return viewer.render()


def new_contest(request):
    viewer = ContestKernel.ContestList(request)
    viewer.new_contest()
    return viewer.render()


def save_new_contest(request):
    viewer = ContestKernel.ContestList(request)
    viewer.save_new_contest()
    return viewer.render()


def contest_body(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.contest_body(cid)
    return viewer.render()


def problems_list(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.problems_list(cid)
    return viewer.render()


def show_problem(request, cid, pid):
    viewer = ContestKernel.ContestBody(request)
    viewer.show_contest_problem(cid, pid)
    return viewer.render()


def contest_submit_code(request, cid, pid):
    viewer = ContestKernel.ContestBody(request)
    viewer.contest_submit_code(cid, pid)
    return viewer.render()


def contest_status(request, cid, page=1):
    viewer = ContestKernel.ContestBody(request)
    viewer.contest_status(cid, int(page))
    return viewer.render()


def contest_rank_list(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.rank_list(cid)
    return viewer.render()


def contest_faq(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.faq(cid)
    return viewer.render()


def contest_faq_new_msg(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.faq_new_msg(cid)
    return viewer.render()


def contest_faq_save_new_msg(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.faq_save_new_msg(cid)
    return viewer.render()


def contest_faq_del(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.faq_del(cid)
    return viewer.render()


def contest_faq_reply_msg(request, cid, fid):
    viewer = ContestKernel.ContestBody(request)
    viewer.faq_reply_msg(cid, fid)
    return viewer.render()


def contest_faq_save_reply(request, cid, fid):
    viewer = ContestKernel.ContestBody(request)
    viewer.faq_save_reply(cid, fid)
    return viewer.render()


# ============================


def contest_mgr_contest_setting(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_contest_setting(cid)
    return viewer.render()


def contest_mgr_user(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_user(cid)
    return viewer.render()


def contest_mgr_read_xls_to_change_team_user_info(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.read_xls_to_change_team_user_info(cid)
    return viewer.render()


def contest_mgr_reset_user_passwd(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_reset_user_passwd(cid)
    return viewer.render()


def contest_mgr_save_contest_setting(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_save_contest_setting(cid)
    return viewer.render()


def contest_mgr_add_new_problems(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_add_new_problems(cid)
    return viewer.render()


def contest_mgr_remove_problems(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_remove_problems(cid)
    return viewer.render()


def contest_mgr_problem_setting(request, cid, pid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_modify_problem_setting(cid, pid)
    return viewer.render()


def contest_mgr_save_problem_setting(request, cid, pid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_save_problem_setting(cid, pid)
    return viewer.render()


def contest_mgr_start_problem_rejudge(request, cid, pid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_start_problem_rejudge(cid, pid)
    return viewer.render()


def contest_mgr_change_status(request, cid, sid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_change_status(cid, sid)
    return viewer.render()


def contest_mgr_save_status_change(request, cid, sid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_save_status_change(cid, sid)
    return viewer.render()


def contest_mgr_lock_contest_user(request, cid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_lock_contest_user(cid)
    return viewer.render()


def contest_mgr_code_analyzer(request, cid, page=1):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_code_analyzer(cid, int(page))
    return viewer.render()


def contest_mgr_code_compare(request, cid, caid):
    viewer = ContestKernel.ContestBody(request)
    viewer.mgr_code_compare(cid, caid)
    return viewer.render()
