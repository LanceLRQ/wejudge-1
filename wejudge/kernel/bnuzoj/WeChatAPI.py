# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import wejudge.kernel.general as kernel
import wejudge.apps.account.models as AccountModel
import urllib2
import json



class WeChatAPI(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)

    def oauth2_callback(self):
        """
        微信Oauth2.0回调处理
        :return:
        """
        code = self._request.GET.get('code', None)
        state = self._request.GET.get('state', '')
        if code is None or code.strip() == '':
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_WECHATAPI_USER_CANCEL_AUTH
            return

        curl = urllib2.urlopen(
            "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"
            % (kernel.const.WECHAT_APP_ID, kernel.const.WECHAT_APP_SECERT, code)
        )
        access_token_info = WeChatAPI.__parse_json(curl.read())

        if access_token_info is None:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_WECHATAPI_UNKNOW_ERROR
            return

        if state == 'login' or state.strip() == '':
            if self._user_session.is_logined():
                self._action = kernel.const.VIEW_ACTION_REDIRECT
                self._redirect_url = '/'
                return

            user = AccountModel.User.objects.filter(wc_openid=access_token_info.get('openid'))
            if not user.exists():
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_WECHATAPI_NEVER_BIND_ANY_USER
                return
            user = user[0]
            user.wc_access_token = access_token_info.get('access_token')
            user.wc_expires_in = access_token_info.get('expires_in')
            user.wc_refresh_token = access_token_info.get('refresh_token')
            user.save()
            self._user_session.start_login(user)
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = '/'
            return

        elif state == 'bind' or state == 'ref_img':
            if not self._user_session.is_logined():
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_WECHATAPI_PLEASE_LOGIN
                return
            user = AccountModel.User.objects.filter(wc_openid=access_token_info.get('openid'))
            if user.exists():
                user = user[0]
                if user.id != self._user_session.user_id:
                    self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                    self._context = kernel.error_const.ERROR_WECHATAPI_USER_BINDED
                    return
            else:
                user = self._user_session.user

            user_info = WeChatAPI.__api_get_user_info(access_token_info.get('openid'), access_token_info.get('access_token'))
            if user_info is None:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_WECHATAPI_UNKNOW_ERROR
                return

            user.wc_openid = access_token_info.get('openid')
            user.wc_access_token = access_token_info.get('access_token')
            user.wc_expires_in = access_token_info.get('expires_in')
            user.wc_refresh_token = access_token_info.get('refresh_token')
            user.wc_user_info = json.dumps(user_info)
            if user.headimg is None or user.headimg.strip() == '':
                headimg = kernel.GeneralTools.save_head_image_from_url(user_info.get('headimgurl'), user.id)
                if headimg is not False:
                    user.headimg = headimg
            if state == 'ref_img':
                headimg = kernel.GeneralTools.save_head_image_from_url(user_info.get('headimgurl'), user.id)
                if headimg is not False:
                    user.headimg = headimg
            user.save()
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = '/account/space/%s#wechat' % user.id
            return

        else:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_WECHATAPI_UNKNOW_STATE
            return


    @staticmethod
    def __api_get_user_info(open_id, access_token):
        """
        读取用户授权信息
        :param access_token_info:
        :return:
        """
        curl = urllib2.urlopen(
            "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN"
            % (access_token, open_id)
        )
        return WeChatAPI.__parse_json(curl.read())

    @staticmethod
    def __parse_json(data):
        """
        解析json
        :param data:
        :return: 如果解析失败，返回None
        """
        try:
            oauth2info = json.loads(data)
            return oauth2info
        except:
            return None