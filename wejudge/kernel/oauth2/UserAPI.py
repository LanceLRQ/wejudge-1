# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import Oauth2Provider
import wejudge.kernel.general as kernel
import wejudge.apps.account.models as AccountModel


class UserAPI(Oauth2Provider.Oauth2Provider):

    def __init__(self, request):
        Oauth2Provider.Oauth2Provider.__init__(self, request)

    def user_info(self):
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        if not self._method_check("POST"):
            return

        openid = self._request.GET.get('openid', '')
        access_token = self._request.GET.get('access_token', '')

        at = self._check_access_token(openid, access_token, 'auth_userinfo')
        if at is False:
            return

        self._context = self._OauthSuccess({
            "open_id": at.open_id,
            "role": at.account.role,
            "sex": at.account.sex,
            "nickname": at.account.nickname,
            "realname": at.account.realname,
            "heading": "https://oj.bnuz.edu.cn/resource/headimg/" + at.account.headimg,
            "motto": at.account.motto,
            "solution_history": {
                'visited': at.account.visited,
                'solved': at.account.solved,
                'submissions': at.account.submissions,
                'accepted': at.account.accepted,
            },
            "exprience": {
                "point": at.account.point_total,
                "level": at.account.level
            }
        })