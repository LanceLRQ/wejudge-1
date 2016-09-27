# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'
import re
import wejudge.kernel.general as kernel
import wejudge.apps.account.models as AccountModel
import ManageProvider as provider
import os
import xlrd
import uuid
import time


class AccountMgr(provider.ManageProvider):

    def __init__(self, request):
        provider.ManageProvider.__init__(self, request)

    def view_list(self, page=1):
        """
        用户账户列表
        :param page:
        :return:
        """
        if not self._check_login():
            return
        if not self._check_permission():
            return

        account_id = self._request.GET.get('account_id', '')
        account_id_type = self._request.GET.get('account_id_type', '')
        account_role = self._request.GET.get('account_role', '')

        desc = self._request.GET.get('desc', '0')
        if desc.strip() == '1':
            desc = True
        else:
            desc = False
        author = "%s%s" % (account_id, account_id_type)

        account_list = self._get_account_list(author, account_role, desc)

        count = account_list.count()

        if count == 0:
            pager_render = ''
            account_list = []
        else:
            pager = kernel.PagerProvider(count, 50, int(page), "cpanel_accountmgr_viewlist", 11, _get=self._request.GET)
            pager_render = pager.render()
            account_list = account_list.all()[pager.start_idx: pager.start_idx + 50]

        self._template_file = "cpanel/account/list.html"
        self._context = {
            'pager': pager_render,
            'account_list': account_list,
            'type': 'account_mgr',
            # filter
            "account_id": account_id,
            "account_id_type": account_id_type,
            "account_role": account_role,
            'desc': desc,
        }

    def modify_account(self, uid):
        """
        编辑账户
        :param uid:账户ID
        :return:
        """
        if not self._check_login(True, True):
            return
        if not self._check_permission(True, True):
            return
        account = AccountModel.User.objects.filter(id=uid)
        if not account.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]账户不存在"
            return
        self._template_file = "cpanel/account/editor.html"
        self._context = {
            'type': 'modify',
            'account': account[0]
        }

    def new_account(self):
        """
        新建账户
        :param uid:账户ID
        :return:
        """
        if not self._check_login(True, True):
            return
        if not self._check_permission(True, True):
            return

        self._template_file = "cpanel/account/editor.html"
        self._context = {
            'type': 'new',
        }

    def save_account(self, uid=None):
        """
        保存账户信息
        :param uid:如果是None则为新建
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if not self._check_permission(True):
            return

        nickname = self._request.POST.get('nickname', '')
        password = self._request.POST.get('password', '')
        email = self._request.POST.get('email', '')
        motto = self._request.POST.get('motto', '')
        role = self._request.POST.get('role', '')
        realname = self._request.POST.get('realname', '')
        locked = self._request.POST.get('locked', '')

        if str(locked.strip()) == '1':
            locked = True
        else:
            locked = False

        if nickname.strip() == '':
            self._result = kernel.RESTStruct(False, u'昵称不能为空！')
            return
        if len(nickname) > 12:
            self._result = kernel.RESTStruct(False, u'昵称不能超过12个字符')
            return

        try:
            role = int(role)
        except:
            role = -1
        if role not in kernel.const.ACCOUNT_ROLE.iterkeys():
            self._result = kernel.RESTStruct(False, u'用户类型不存在！')
            return

        if uid is None:
            user_id = self._request.POST.get('user_id', '')
            check = re.match("\w+", user_id)
            if check is None:
                self._result = kernel.RESTStruct(False, u'用户名称不符合规范！')
                return
            account = AccountModel.User.objects.filter(id=user_id)
            if account.exists():
                self._result = kernel.RESTStruct(False, msg=u"账户已经存在")
                return
            account = AccountModel.User()
            if password.strip() != '':
                account.password = self._user_session.gen_passwd(password)
            else:
                account.password = self._user_session.gen_passwd("123456")
            account.create_time = int(time.time())
            account.id = user_id
            account.save()
        else:
            account = AccountModel.User.objects.filter(id=uid)
            if not account.exists():
                self._result = kernel.RESTStruct(False, msg=u"账户不存在")
                return
            account = account[0]
            nns = AccountModel.User.objects.filter(nickname=nickname)
            for ns in nns:
                if ns.id != account.id:
                    self._result = kernel.RESTStruct(False, u'当前昵称已经存在，请更换！')
                    return
            if email.strip() != "":

                nns = AccountModel.User.objects.filter(email=email)
                for ns in nns:
                    if ns.id != account.id:
                        self._result = kernel.RESTStruct(False, u'当前Email已经存在，请更换！')
                        return

            if password.strip() != '':
                account.password = self._user_session.gen_passwd(password)

        if email != account.email:
            account.email_validated = False
            account.email_findpwd_validated = ''

        account.locked = locked
        account.nickname = nickname
        account.realname = realname
        account.role = role
        account.motto = motto
        account.email = email
        account.save()
        self._result = kernel.RESTStruct(True)

    def reset_password(self):
        """
        批量重置密码
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if not self._check_permission(True):
            return

        msg = []

        account_ids = self._request.POST.getlist("account_ids")
        if len(account_ids) == 0:
            self._result = kernel.RESTStruct(False, msg="无操作项目")
            return
        for id in account_ids:
            account = AccountModel.User.objects.filter(id=id)
            if not account.exists():
                msg.append("[%s]不存在" % id)
                continue
            account = account[0]
            account.password = kernel.LoginSession.gen_passwd("123456")
            account.save()

        if len(msg) > 0:
            self._result = kernel.RESTStruct(True, msg="操作成功，但是以下项目没有改动：<br />%s" % "<br />".join(msg))
        else:
            self._result = kernel.RESTStruct(True, msg="操作成功")

    def delete_account(self):
        """
        删除账户
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if not self._check_permission(True):
            return

        msg = []

        account_ids = self._request.POST.getlist("account_ids")
        if len(account_ids) == 0:
            self._result = kernel.RESTStruct(False, msg="无操作项目")
            return
        for id in account_ids:
            account = AccountModel.User.objects.filter(id=id)
            if not account.exists():
                msg.append("[%s]不存在" % id)
                continue
            account = account[0]
            account.delete()

        if len(msg) > 0:
            self._result = kernel.RESTStruct(True, msg="操作成功，但是以下项目没有改动：<br />%s" % "<br />".join(msg))
        else:
            self._result = kernel.RESTStruct(True, msg="操作成功")

    def get_filter_page(self):
        """
        获取过滤器列表
        :return:
        """
        account_id = self._request.GET.get('account_id', '')
        account_id_type = self._request.GET.get('account_id_type', '')
        account_role = self._request.GET.get('account_role', '')
        desc = self._request.GET.get('desc', '')

        if str(desc.strip()) == '1':
            desc = True
        else:
            desc = False

        self._template_file = "cpanel/account/filter.html"
        self._context = {
            "account_id": account_id,
            "account_id_type": account_id_type,
            "account_role": account_role,
            'desc': desc,
            "role_called": kernel.const.ACCOUNT_ROLE_CALLED
        }

    def import_account_view(self):
        """
        导入账号页面
        :return:
        """
        if not self._check_login():
            return
        if not self._check_permission():
            return

        self._template_file = "cpanel/account/import.html"
        self._context = {
            'type': 'account_import',
        }

    def import_account(self):
        """
        账号导入处理程序
        :return:
        """
        self._template_file = "cpanel/account/import_result.html"
        role = self._request.POST.get('role', "")
        try:
            role = int(role)
            if role not in kernel.ACCOUNT_ROLE.keys():
                return
        except:
            return

        result = []
        outdata = {}

        files = self._request.FILES.get('upload_xls')
        if files is None:
            self._context = {
                "msg": "请选择要上传的XLS文件",
                "msg_color": "danger"
            }
            return
        else:
            path = "account_import_xls/%s%s" % (uuid.uuid4(), '.xls')
            file_name = os.path.join(kernel.const.IMPORT_PROCESS_TEMP_DIR, path)
            destination = open(file_name, 'wb+')
            for chunk in files.chunks():
                destination.write(chunk)
            destination.close()
            try:
                xls_sheet = xlrd.open_workbook(file_name)
                xls_table = xls_sheet.sheet_by_index(0)
                if xls_table.nrows <= 2:
                    self._context = {
                        "msg": "没有需要处理的数据",
                        "msg_color": "warning"
                    }
                    return
                for i in range(2, xls_table.nrows):
                    user_row = xls_table.row_values(i)
                    if len(user_row) == 1:
                        continue
                    uid = user_row[0]
                    uname = user_row[1]
                    if (uid.strip() == "") or (uname.strip() == ""):
                        continue
                    if len(user_row) == 3:
                        urealname = user_row[2]
                    else:
                        urealname = uname

                    if urealname == '':
                        urealname = uname

                    user = AccountModel.User.objects.filter(id=uid.strip())
                    if user.exists():
                        user = user[0]
                        user.nickname = uname
                        user.realname = urealname
                        user.role = role
                        user.save()
                        result.append({
                            "color": "warning",
                            "status": 1,
                            "id": user.id,
                            "nickname": user.nickname,
                            "realname": user.realname,
                            "role": user.role,
                        })
                    else:
                        user = AccountModel.User()
                        user.id = uid
                        user.password = self._user_session.gen_passwd(uid)
                        user.nickname = uname
                        user.realname = urealname
                        user.role = role
                        user.create_time = int(time.time())
                        user.save()
                        result.append({
                            "color": "success",
                            "status": 0,
                            "id": user.id,
                            "nickname": user.nickname,
                            "realname": user.realname,
                            "role": user.role,
                        })
            except Exception, ex:
                print str(ex)
                self._context = {
                    "result": result,
                    "msg": "XLS文件处理过程出现错误，请检查XLS文件是否填写正确。以下如果有结果数据，则是显示已经处理成功的项目",
                    "msg_color": "danger"
                }
                return

            self._context = {
                "result": result,
                "msg": "处理完成",
                "msg_color": "success"
            }
            return

    def _get_account_list(self, author_id=None, role=None, desc=False):

        account_list = AccountModel.User.objects.all()
        if (author_id is not None) and (author_id.strip() != ""):
            if author_id[:3] == '[n]':
                account_list = account_list.filter(nickname__contains=author_id[3:])
            elif author_id[:3] == '[r]':
                account_list = account_list.filter(realname__contains=author_id[3:])
            else:
                account_list = account_list.filter(id__contains=author_id)

        if (role is not None) and (role.strip() != ""):
            account_list = account_list.filter(role=role)

        if desc:
           account_list = account_list.order_by('-id')

        return account_list