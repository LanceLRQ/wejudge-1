# -*- coding: utf-8 -*-
# coding:utf-8


import const
import RestStruct as RS
import LocalStorage as LS
import LoginSession as LUS
import error_const
import WebConfiguration as WC
import django.shortcuts
import django.http.response
import django.core.urlresolvers

__author__ = 'lancelrq'


class ViewerFramework(object):
    """视图渲染框架"""

    def __init__(self, request):
        """
        初始化视图渲染框架
        :param request: 传入django的request对象
        :return:
        """
        self._request = request                                  # http Request Object
        self._content_type = const.VIEW_CONTENT_TYPE_DEFAULT     # (仅在登陆请求发生时)渲染内容格式 (redirect | text | json)
        self._action = const.VIEW_ACTION_RENDER                  # 渲染模式 (render | redirect | login_req | error_page | json | http_error | none)
        self._template_file = ''                                 # 渲染模板文件位置、下载文件的原始名称
        self._download_filename = ''                             # 下载文件的展示名称
        self._context = {}                                       # 渲染内容(将被提交到django框架的Context类中)
        self._result = None                                      # JSON渲染内容
        self._redirect_url = ''                                  # 请求跳转路径
        self._user_session = LUS.LoginSession(request)           # 用户登陆会话
        self._config = WC.WebConfiguration()                     # 用户配置信息
        self._cookie_resp = []                                   # 响应Cookies
        self._navbar_action = "index"                            # 导航栏激活
        self._resp_http_status_code = 200                        # HTTP响应Code
        pass

    def add_cookie(self, cookie):
        if isinstance(self._cookie_resp, list) and isinstance(cookie, list):
            self._cookie_resp.extend(cookie)

    def _check_login(self, ajax=False, no_redirect=False):
        """登陆检查（含渲染设置）"""
        if not self._user_session.is_logined():
            self._action = const.VIEW_ACTION_LOGIN_REQUEST
            if ajax:
                if no_redirect:
                    self._content_type = const.VIEW_CONTENT_TYPE_TEXT
                else:
                    self._content_type = const.VIEW_CONTENT_TYPE_JSON
            else:
                if no_redirect:
                    self._content_type = const.VIEW_CONTENT_TYPE_TEXT
                else:
                    self._content_type = const.VIEW_CONTENT_TYPE_DEFAULT
            self._redirect_url = self._request.path
            return False
        return True

    def render(self):
        if isinstance(self._cookie_resp, list):
            if len(self._cookie_resp) == 0:
                return self.__render()
            else:
                resp = self.__render()
                for c in self._cookie_resp:
                    resp.set_cookie(
                        key=c.get('key'),
                        value=c.get('value'),
                        max_age=c.get('max_age'),
                        expires=c.get('expires'),
                        path=c.get('path'),
                        domain=c.get('domain'),
                        secure=c.get('secure'),
                        httponly=c.get('httponly')
                    )
                return resp
        else:
            return self.__render()

    def __render(self):
        """
        执行渲染程序
        :return:
        """

        if self._action == const.VIEW_ACTION_REDIRECT:             # 重定向模式
            return django.http.response.HttpResponseRedirect(self._redirect_url)

        elif self._action == const.VIEW_ACTION_LOGIN_REQUEST:           # 登陆请求跳转模式
            try:

                if self._content_type == const.VIEW_CONTENT_TYPE_JSON:           # json
                        return django.http.response.HttpResponse(
                                RS.RESTStruct(False, '', None, 'login_req').dump(),
                                status_code=self._resp_http_status_code
                        )

                elif self._content_type == const.VIEW_CONTENT_TYPE_TEXT:         # 文本模式
                    return django.http.response.HttpResponse("[ERROR]请先登录!", status=self._resp_http_status_code)

                else:                                       # 正常模式(跳转)
                    url = self._request.get_full_path()
                    return django.http.response.HttpResponseRedirect("%s?referer=%s" % ("/", url))

            except Exception, ex:
                    return django.http.response.HttpResponse(str(ex), status=500)

        elif self._action == const.VIEW_ACTION_RENDER:             # 渲染模式
                if self._template_file == '':
                    return django.http.response.HttpResponse("", status=self._resp_http_status_code)
                context = {
                    "web_config": self._config,
                    "user_session": self._user_session,
                    "request": self._request,
                    "navbar_action": self._navbar_action
                }
                if isinstance(self._context, dict):
                    context.update(self._context)
                return django.shortcuts.render_to_response(self._template_file, context)

        elif self._action == const.VIEW_ACTION_JSON:               # json

            if (self._result is None) or (not isinstance(self._result, RS.RESTStruct)):
                return django.http.response.HttpResponse(
                        RS.RESTStruct(False, 'IllegalArgumentException:`_result` Not a \'RESTStruct\' object', None, '').dump(),
                        status_code=self._resp_http_status_code
                )
            return django.http.response.HttpResponse(self._result.dump(), status=self._resp_http_status_code)

        elif self._action == const.VIEW_ACTION_ERROR_PAGE:         # 错误页面
            context = {
                "errbody": error_const.ERROR_UNKNOW,
                "web_config": self._config,
                "user_session": self._user_session,
                "request": self._request,
                "navbar_action": self._navbar_action
            }
            if isinstance(self._context, dict):
                context['errbody'] = self._context
            return django.shortcuts.render_to_response("errpage.html", context)

        elif self._action == const.VIEW_ACTION_DOWNLOAD:            # 下载模式

            if not isinstance(self._context, LS.LocalStorage):
                 return django.http.response.HttpResponse("下载文件处理失败", status=500)

            def read_file(f, buf_size=262144):
                try:
                    while True:
                        c = f.read(buf_size)
                        if c:
                            yield c
                        else:
                            break
                    f.close()
                except BaseException, ex:
                    yield "下载文件处理失败"

            if self._download_filename == '':
                self._download_filename = self._template_file

            resp = django.http.response.HttpResponse(
                    read_file(self._context.open_file(self._template_file, 'rb'))
            )
            resp['Content-Type'] = 'application/octet-stream'
            resp['Content-Disposition'] = 'attachment; filename=%s' % self._download_filename
            return resp

        else:                                       # 纯文本模式

            if isinstance(self._context, str):
                return django.http.response.HttpResponse(self._context, status=self._resp_http_status_code)
            else:
                try:
                    return django.http.response.HttpResponse(str(self._context), status=self._resp_http_status_code)
                except Exception, ex:
                    return django.http.response.HttpResponse("Cannot found a string object.", status=500)
