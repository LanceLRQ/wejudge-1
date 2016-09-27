# -*- coding: utf-8 -*-
# coding:utf-8
import wejudge.kernel.general as kernel
__author__ = 'lancelrq'


class ManageProvider(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)

    def _check_permission_only(self):
        """
        检查权限
        :return:
        """
        if self._user_session.user_role == 99:
            return True
        else:
            return False

    def _check_permission(self, ajax=False, no_redirect=False):
        """
        检查权限（包含渲染数据处理，也就是说调用完的结果为False时只要return即可，不必再写渲染代码）
        :ajax problem: 是否为ajax请求
        :param no_redirect: 禁用错误页面跳转
        :return:
        """
        flag = self._check_permission_only()
        if flag is False:
            if no_redirect:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "[ERROR]当前账户没有操作权限"
                return flag
            if ajax:
                self._action = kernel.const.VIEW_ACTION_JSON
                self._result = kernel.RESTStruct(False, u'当前账户没有操作权限')
                return flag
            else:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ADMIN_PERMISSION_DENIED
                return flag
        return flag