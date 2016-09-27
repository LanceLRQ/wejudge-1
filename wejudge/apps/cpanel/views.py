from django.shortcuts import render
import wejudge.kernel.cpanel as CPanelKernel
# Create your views here.


def index(request):
    view = CPanelKernel.GeneralMgr(request)
    view.index()
    return view.render()


def web_config(request):
    view = CPanelKernel.GeneralMgr(request)
    view.web_config()
    return view.render()


def save_web_config(request):
    view = CPanelKernel.GeneralMgr(request)
    view.save_web_config()
    return view.render()


# =========== Account Mgr =================


def accountmgr_view_list(request, page=1):
    view = CPanelKernel.AccountMgr(request)
    view.view_list(int(page))
    return view.render()


def accountmgr_view_list_filter(request):
    view = CPanelKernel.AccountMgr(request)
    view.get_filter_page()
    return view.render()


def accountmgr_import_account(request):
    view = CPanelKernel.AccountMgr(request)
    view.import_account_view()
    return view.render()


def accountmgr_import_account_upload(request):
    view = CPanelKernel.AccountMgr(request)
    view.import_account()
    return view.render()


def accountmgr_modify_account(request, uid):
    view = CPanelKernel.AccountMgr(request)
    view.modify_account(uid)
    return view.render()


def accountmgr_new_account(request):
    view = CPanelKernel.AccountMgr(request)
    view.new_account()
    return view.render()


def accountmgr_save_modify_account(request, uid):
    view = CPanelKernel.AccountMgr(request)
    view.save_account(uid)
    return view.render()


def accountmgr_save_new_account(request):
    view = CPanelKernel.AccountMgr(request)
    view.save_account()
    return view.render()


def accountmgr_reset_password(request):
    view = CPanelKernel.AccountMgr(request)
    view.reset_password()
    return view.render()


def accountmgr_delete_account(request):
    view = CPanelKernel.AccountMgr(request)
    view.delete_account()
    return view.render()
