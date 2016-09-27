# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
import wejudge.apps.contest.models as ContestModel
from django.core.urlresolvers import reverse
__author__ = 'lancelrq'


class ContestList(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'contest'

    def contest_index(self):
        self._redirect_url = reverse("contest_list", args=(1, ))
        self._action = kernel.VIEW_ACTION_REDIRECT
        # self._template_file = "contest/acm/2016IT_result.html"

    def contest_list(self, page=None, limit=30):

        contest_list = ContestModel.Contest.objects.order_by("-id")

        count = contest_list.count()

        if count == 0:
            pager_render = ''
        else:
            pager = kernel.PagerProvider(count, limit, page, "contest_list", 11, _get=self._request.GET)
            contest_list = contest_list.all()[pager.start_idx: pager.start_idx + limit]
            pager_render = pager.render()

        detail_view = {}

        for contest in contest_list:
            detail_view[contest.id] = {
                "title": contest.title,
                "description": contest.description,
                "start_time": contest.start_time,
                "end_time": contest.end_time,
                "author": contest.author.nickname,
                "lang": contest.lang
            }

        self._template_file = "contest/list.html"
        self._context = {
            "detail_view": detail_view,
            "contesnt_list": contest_list,
            "pager": pager_render
        }

    def new_contest(self):
        """
        创建在线比赛
        :return:
        """
        if not self._check_login():
            return
        self._template_file = "contest/new_contest.html"
        self._context = {

        }

    def save_new_contest(self):
        """
        创建比赛
        :return:
        """
        if not self._check_login():
            return
        if self._user_session.user_role not in [2, 99]:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_ADMIN_PERMISSION_DENIED
            return
        title = self._request.POST.get('title', '')
        agree = self._request.POST.get('agree', '')

        if agree != '1':
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_CONTEST_NEW_REQUIRE_AGREEMENT
            return
        if title.strip() == '':
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_CONTEST_REQUIRE_TITLE
            return

        contest = ContestModel.Contest()
        contest.title = title
        contest.author = self._user_session.entity
        contest.user_limit = ''
        contest.save()
        self._action = kernel.const.VIEW_ACTION_REDIRECT
        self._redirect_url = reverse('contest_mgr_contest_setting', args=(contest.id,))
        return
