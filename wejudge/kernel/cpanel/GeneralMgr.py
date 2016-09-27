# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'
import wejudge.kernel.general as kernel
import ManageProvider as provider
import django.core.urlresolvers


class GeneralMgr(provider.ManageProvider):

    def __init__(self, request):
        provider.ManageProvider.__init__(self, request)

    def index(self):
        self._action = kernel.const.VIEW_ACTION_REDIRECT
        self._redirect_url = django.core.urlresolvers.reverse("cpanel_web_config")
        # if not self._check_login():
        #    return
        # if not self._check_permission():
        #     return
        # self._template_file = "cpanel/index.html"
        # self._context = {
        #     'type': 'index'
        # }

    def web_config(self):
        if not self._check_login():
           return
        if not self._check_permission():
            return
        self._template_file = "cpanel/general/editor.html"
        self._context = {
            'type': 'web_config',
            'year_terms': kernel.GeneralTools.get_year_terms()
        }

    def save_web_config(self):
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return
        if not self._check_permission(True):
            return

        web_title = self._request.POST.get("web_title", "")
        web_keyword = self._request.POST.get("web_keyword", "")
        web_desc = self._request.POST.get("web_desc", "")
        web_version = self._request.POST.get("web_version", "")
        web_notice = self._request.POST.get("web_notice", "")
        web_stop_judging = self._request.POST.get("web_stop_judging", "")
        web_fixing = self._request.POST.get("web_fixing", "")
        web_register = self._request.POST.get("web_register", "")
        web_pwd_equal_username = self._request.POST.get("web_pwd_equal_username", "")
        web_login_limit = self._request.POST.get("web_login_limit", "")
        web_login_white_list = self._request.POST.get("web_login_white_list", "")
        web_login_black_list = self._request.POST.get("web_login_black_list", "")
        year = self._request.POST.get("year", "")
        term = self._request.POST.get("term", "")

        if web_title.strip() == "":
            self._result = kernel.RESTStruct(False, "请输入网站标题！")
            return

        if str(web_stop_judging) == '1':
            web_stop_judging = True
        else:
            web_stop_judging = False

        if str(web_fixing) == '1':
            web_fixing = True
        else:
            web_fixing = False

        if str(web_login_limit) == '1':
            web_login_limit = True
        else:
            web_login_limit = False

        if str(web_register) == '1':
            web_register = True
        else:
            web_register = False

        if str(web_pwd_equal_username) == '1':
            web_pwd_equal_username = True
        else:
            web_pwd_equal_username = False

        try:
            year = int(year)
            term = int(term)
        except:
            self._result = kernel.RESTStruct(False, "学年学期数据有误！")
            return

        self._config.web_title = web_title
        self._config.web_keyword = web_keyword
        self._config.web_desc = web_desc
        self._config.web_version = web_version
        self._config.web_notice = web_notice
        self._config.web_fixing = web_fixing
        self._config.web_register = web_register
        self._config.web_stop_judging = web_stop_judging
        self._config.web_login_limit = web_login_limit
        self._config.web_login_white_list = web_login_white_list
        self._config.web_login_black_list = web_login_black_list
        self._config.web_pwd_equal_username = web_pwd_equal_username
        self._config.year = year
        self._config.term = term
        self._config.save()
        self._result = kernel.RESTStruct(True)
