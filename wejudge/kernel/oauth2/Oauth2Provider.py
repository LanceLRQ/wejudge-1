# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import json
import uuid
import time
import hashlib
import base64
import wejudge.apps.oauth2.models as Oauth2Model
import wejudge.kernel.general as kernel

class Oauth2Provider(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)


    def _OauthError(self, err_code, err_msg):

        return json.dumps({
            'errcode': err_code,
            'errmsg': err_msg
        })

    def _OauthSuccess(self, data):
        return json.dumps({
            'errcode': 0,
            'errmsg': 'ok'
        }.update(data))

    def _method_check(self, method='POST'):
        """
        检查请求方法
        :return:
        """
        if not self._request.method.upper() == method:
            self._resp_http_status_code = 405
            self._context = "Not allow this method."
            return False
        return True

    def _create_open_id(self, client_id, user_id):
        """
        生成OpenID
        :param client_id:
        :param user_id:
        :return:
        """
        strkey = "%s_%s" % (client_id, user_id)
        sha = hashlib.sha1()
        sha.update(strkey)
        open_id = "bnuz_" + base64.b64encode(sha.digest())
        return open_id

    def _is_user_allow(self, client, user):
        """
        检查用户是否同意授权
        :return:
        """
        uu = Oauth2Model.UserAllowClient.objects.filter(client=client, account=user)
        if uu.exists():
            uu = uu[0]
            if uu.is_allow:
                return uu.open_id
            else:
                return False
        else:
            return False

    def _gen_access_token(self, client, user):
        """
        计算Access Token
        :param client:
        :param user:
        :return:
        """
        raw = "<%s>%s,%s(%s)" % (client.app_id, user.id, uuid.uuid4(), time.time())
        sha256 = hashlib.sha256()
        sha256.update(raw)
        return base64.b64encode(sha256.digest())

    def _gen_refresh_token(self, client, user):
        """
        计算Refresh Token
        :param client:
        :param user:
        :return:
        """
        raw = "<%s>%s?%s(%s)" % (client.app_id, user.id, uuid.uuid4(), time.time())
        sha512 = hashlib.sha512()
        sha512.update(raw)
        return base64.b64encode(sha512.digest())

    def _gen_open_id(self, client, user):
        """
        计算openid
        :param client:
        :param user:
        :return:
        """
        raw = "<%s>%s(%s)" % (client.app_id, user.id, uuid.uuid4())
        sha1 = hashlib.sha1()
        sha1.update(raw)
        return "wj_%s" % base64.b64encode(sha1.digest())

    def _gen_authorize_code(self, client, user):
        """
        计算auth code
        :param client:
        :param user:
        :return:
        """
        code = "<%s>%s-%s(%s)" % (client.id, uuid.uuid4(), user.id, time.time())
        sha1 = hashlib.sha1()
        sha1.update(code)
        return sha1.hexdigest()

    def _create_authorize_code(self, client, scopes):
        """
        创建授权码（10分钟有效）
        :return:
        """
        ac = Oauth2Model.AuthCode.objects.filter(client=client, account=self._user_session.entity)
        if not ac.exists():
            ac = Oauth2Model.AuthCode()
            ac.client = client
            ac.account = self._user_session.entity
            ac.save()
        else:
            ac = ac[0]

        ac.code = self._gen_authorize_code(client, ac.account)
        ac.expires_at = int(time.time()) + 600
        ac.scopes = scopes
        ac.save()
        return ac.code

    def _check_user_allow(self, client, user):
        """
        检验用户是否授权，如果同意，则返回Open_id
        :param client:
        :param user:
        :return:
        """
        rel = self._is_user_allow(client, user)
        if rel is not False:
            self._context = self._OauthError(40007, "User Not All This Authorize Method.")
            return
        else:
            return rel

    def _check_access_token(self, openid, access_token, scope='auth_base'):
        """
        检查Access Token
        :param openid:
        :param access_token:
        :return:
        """
        at = Oauth2Model.Tokens.objects.filter(open_id=openid, access_token=access_token)
        if not at.exists():
            self._context = self._OauthError(40007, "Invalid Access Token.")
            return False

        else:
            at = at[0]

            # 检查用户是否允许
            open_id = self._check_user_allow(at.client, at.account)
            if open_id is False:
                return False
            elif open_id != at.open_id:
                self._context = self._OauthError(40009, "Invalid Open ID.")
                return False

            if int(time.time()) >= at.expires_at:
                self._context = self._OauthError(40007, "Invalid Access Token.")
                return False

            if scope == 'auth_base':
                if not at.scopes in ('auth_full', 'auth_userinfo', 'auth_base'):
                    self._context = self._OauthError(40010, "Invalid Scope.")
                    return
            elif scope == 'auth_userinfo':
                if not at.scopes in ('auth_full', 'auth_userinfo'):
                    self._context = self._OauthError(40010, "Invalid Scope.")
                    return
            elif scope == 'auth_full':
                if not at.scopes in ('auth_full',):
                    self._context = self._OauthError(40010, "Invalid Scope.")
                    return

            return at
