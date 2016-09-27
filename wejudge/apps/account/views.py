from django.shortcuts import render
import wejudge.kernel.account as AccountKernel
# Create your views here.

def RankList(request, page=1):
    viewer = AccountKernel.RankList(request)
    viewer.RankList(int(page))
    return viewer.render()

def login(request):
    viewer = AccountKernel.Account(request)
    viewer.login()
    return viewer.render()


def register(request):
    viewer = AccountKernel.Account(request)
    viewer.register()
    return viewer.render()


def save_register(request):
    viewer = AccountKernel.Account(request)
    viewer.save_register()
    return viewer.render()


def save_register_student(request):
    viewer = AccountKernel.Account(request)
    viewer.save_register_student()
    return viewer.render()


def login_ajax(request):
    viewer = AccountKernel.Account(request)
    viewer.login_ajax()
    return viewer.render()


def logout(request):
    viewer = AccountKernel.Account(request)
    viewer.login_out()
    return viewer.render()


def api_check_login(request):
    viewer = AccountKernel.Account(request)
    viewer.check_login()
    return viewer.render()


def find_pwd_start(request):
    viewer = AccountKernel.Account(request)
    viewer.find_pwd_start()
    return viewer.render()


def find_pwd_final(request):
    viewer = AccountKernel.Account(request)
    viewer.find_pwd_final()
    return viewer.render()


# === space ===


def space(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.space(uid)
    return viewer.render()


def user_detail(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.user_detail(uid)
    return viewer.render()


def user_modify(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.user_modify()
    return viewer.render()


def save_user_modify(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.save_user_modify()
    return viewer.render()


def user_avatar(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.user_avatar()
    return viewer.render()


def save_user_avatar(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.save_user_avatar(uid)
    return viewer.render()


def user_wechat(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.user_wechat()
    return viewer.render()


def email_vaild(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.email_vaild()
    return viewer.render()


def email_vaild_check(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.email_vaild_check()
    return viewer.render()


def user_wechat_unbind(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.user_wechat_unbind()
    return viewer.render()


def user_wechat_refresh_headimg(request, uid):
    viewer = AccountKernel.AccountSpace(request)
    viewer.user_wechat_refresh_headimg()
    return viewer.render()


def change_preference_problem_detail_list(request, mode):
    viewer = AccountKernel.AccountSpace(request)
    viewer.change_preference_problem_detail_list(mode)
    return viewer.render()

