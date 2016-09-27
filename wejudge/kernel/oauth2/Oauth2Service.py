# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import time
import wejudge.apps.oauth2.models as Oauth2Model
import wejudge.kernel.general as kernel
import Oauth2Provider


class Oauth2Service(Oauth2Provider.Oauth2Provider):

    def __init__(self, request):
        Oauth2Provider.Oauth2Provider.__init__(self, request)

    def authorize(self):
        """
        引导授权页面
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_DEFAULT

        appid = self._request.GET.get('appid', '')
        redirect_uri = self._request.GET.get('redirect_uri', '')
        response_type = self._request.GET.get('response_type', '')
        scope = self._request.GET.get('scope', '')
        state = self._request.GET.get('state', '')

        client = Oauth2Model.Client.objects.filter(app_id=appid)
        if not client.exists():
            self._context = self._OauthError(40001, "Invalid APP Id.")          # APP Id错误
            return

        client = client[0]

        if client.redirect_uris != redirect_uri:
            self._context = self._OauthError(40001, "Redirect Uri no match.")
            return
        if response_type != 'code':
            self._context = self._OauthError(40002, "Invalid Response Type.")
            return
        if scope not in ('auth_base', 'auth_userinfo', 'auth_full'):
            self._context = self._OauthError(40003, "Invalid Scope Require.")
            return

        try:
            if self._request.method.upper() == 'GET':

                if self._is_user_allow(client, self._user_session.entity) is not False:     # 如果用户已经同意过授权（直接回调）

                    code = self._create_authorize_code(client, scope)
                    self._action = kernel.const.VIEW_ACTION_REDIRECT
                    self._redirect_url = "%s?code=%s" % (client.redirect_uris, code)
                    return

                self._action = kernel.const.VIEW_ACTION_RENDER
                self._template_file = 'oauth2/authorize.html'
                self._context = {
                    "app": client,
                    "appid": appid,
                    "redirect_uri": redirect_uri,
                    "response_type": response_type,
                    "scope": scope,
                    "state": state,
                    "urlcall": self._request.GET.urlencode()
                }
                return

            elif self._request.method.upper() == 'POST':

                uu = Oauth2Model.UserAllowClient.objects.filter(client=client, account=self._user_session.entity)
                if uu.exists():
                    uu = uu[0]
                else:
                    uu = Oauth2Model.UserAllowClient()
                    uu.client = client
                    uu.account = self._user_session.entity
                    uu.open_id = self._gen_open_id(client, self._user_session.entity)
                    uu.save()

                confirm = self._request.POST.get('confirm', '1')
                if confirm != '1':
                    confirm = False
                else:
                    confirm = True

                uu.is_allow = confirm
                uu.save()

                if uu.is_allow:
                    code = self._create_authorize_code(client, scope)
                    self._action = kernel.const.VIEW_ACTION_REDIRECT
                    self._redirect_url = "%s?code=%s" % (client.redirect_uris, code)
                    return
                else:
                    self._action = kernel.const.VIEW_ACTION_REDIRECT
                    self._redirect_url = client.cancel_redirect_uri
                    return

            else:
                self._resp_http_status_code = 405
                self._context = "Not allow this method."
        except Exception, ex:
                self._resp_http_status_code = 500
                self._context = "Oauth API Error."

    def access_token(self):
        """
        用code换取access token
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        if not self._method_check("POST"):
            return

        appid = self._request.GET.get('appid', '')
        appsecert = self._request.GET.get('secret', '')
        code = self._request.GET.get('code', '')
        grant_type = self._request.GET.get('grant_type', '')

        client = Oauth2Model.Client.objects.filter(app_id=appid)
        if not client.exists():
            self._context = self._OauthError(40001, "Invalid APP Id.")          # APP Id错误
            return
        client = client[0]

        if grant_type != 'authorization_code':
            self._context = self._OauthError(40004, "Invalid Grant Type.")
            return

        if appsecert != client.app_secert:
            self._context = self._OauthError(40005, "Invalid App Secert.")
            return

        ac = Oauth2Model.AuthCode.objects.filter(client=client, code=code)
        if not ac.exists():
            self._context = self._OauthError(40006, "Invalid Authorize Code.")
            return
        ac = ac[0]
        if ac.expires_at < int(time.time()):
            self._context = self._OauthError(40006, "Invalid Authorize Code.")
            return

        user = ac.account

        # 检查用户是否允许
        open_id = self._check_user_allow(client, user)
        if open_id is False:
            return

        # create a access token
        at = Oauth2Model.Tokens.objects.filter(client=client, account=user, open_id=open_id, scopes=ac.scopes)
        if not at.exists():
            at = Oauth2Model.Tokens()
            at.client = client
            at.account = user
            at.open_id = open_id
            at.scopes = ac.scopes
            at.save()
        else:
            at = at[0]

        if int(time.time()) >= at.expires_at:   # 如果access_token超出了可用时间
            at.access_token = self._gen_access_token(client, user)
            # Refresh Token的有效规则是建立在Access Token有效的基础上的
            # 当AccessToken失效后，RefreshToken自动失效
            at.refresh_token = self._gen_refresh_token(client, user)
            at.expires_at = int(time.time()) + client.at_expires_time
            at.save()

        ac.delete()

        self._context = self._OauthSuccess({
            "access_token": at.access_token,
            "expires_in": client.at_expires_time,           # 返回客户允许的过期时长
            "expires_at": at.expires_at,                    # 返回过期时间的服务器时间戳
            "refresh_token": at.refresh_token,
            "openid": open_id,
            "scope": ac.scopes
        })

    def valid_token(self):
        """
        返回Access Token是否有效
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        if not self._method_check("POST"):
            return

        openid = self._request.GET.get('openid', '')
        access_token = self._request.GET.get('access_token', '')

        at = self._check_access_token(openid, access_token)
        if at is False:
            return

        self._context = self._OauthSuccess({})

    def refresh_token(self):
        """
        刷新Access Token
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        if not self._method_check("POST"):
            return

        openid = self._request.GET.get('openid', '')
        access_token = self._request.GET.get('access_token', '')
        refresh_token = self._request.GET.get('refresh_token', '')

        at = self._check_access_token(openid, access_token)
        if at is False:
            return

        if at.refresh_token is None or at.refresh_token == '':
            self._context = self._OauthError(40008, "Invalid Refresh Token.")
            return
        if at.refresh_token != refresh_token:
            self._context = self._OauthError(40008, "Invalid Refresh Token.")
            return

        at.expires_at = int(time.time()) + at.client.rt_expires_time
        at.refresh_token = ""
        at.save()

        self._context = self._OauthSuccess({
            "openid": at.open_id,
            "expires_in": at.client.rt_expires_time,            # 返回客户允许的过期时长
            "expires_at": at.expires_at                         # 返回过期时间的服务器时间戳
        })
