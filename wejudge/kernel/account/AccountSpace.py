# -*- coding: utf-8 -*-
# coding:utf-8
import django.conf
import wejudge.apps.account.models as AccountModel
import wejudge.apps.problem.models as ProblemModel
import wejudge.apps.asgn.models as AsgnModel
import wejudge.apps.bnuzoj.models as WebModel
import wejudge.kernel.general as kernel
from django.db import connection
import time
from django.core.urlresolvers import reverse
from wejudge.kernel.general import ESConnector
import os
import re
import sys
import string
import smtplib
import base64
import uuid
import hashlib
from PIL import Image as image
import django.core.urlresolvers
__author__ = 'lancelrq'


class AccountSpace(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'account'

    def space(self, user_id):
        """
        展示用户信息界面
        :param user_id:
        :return:
        """
        if not self._check_login():
            return
        user = self._get_user(user_id)
        if user_id is None:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_USER_NOT_FOUND
            return
        if user.id[0:4] == 'team':
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = django.core.urlresolvers.reverse("problem_archive")
            return

        self._template_file = "account/space.html"
        self._context = {
            'account': user
        }

    def user_detail(self, user_id):
        """
        用户详细信息
        :param user_id:
        :return:
        """
        if not self._check_login(True, True):
            self._context = "请先登录"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        user = self._get_user(user_id)
        if user_id is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到用户"
            return

        ## 统计部分已经转移到判题机队列了
        # pv = user.problemvisited_set
        # count = ProblemModel.JudgeStatus.objects.filter(author_id=user_id).count()
        # if int(user.submissions) != int(count):
        #     user.submissions = int(count)
        #     user.accepted = ProblemModel.JudgeStatus.objects.filter(author__id=user_id, flag=0).count()
        #     user.visited = pv.count()
        #     user.solved = pv.filter(accepted__gt=0).count()
        # user.point_solved = user.solved * 2
        # user.save()

        require_change_pwd = False
        asgn_list = []
        if user.id == self._user_session.user_id:
            # === PWD CHECK ===
            PWD_CHECK_LIST = [
                self._user_session.gen_passwd(user.id),
                self._user_session.gen_passwd('123456')
            ]
            if user.password in PWD_CHECK_LIST:
                require_change_pwd = True
            access_list = AsgnModel.AsgnAccessControl.objects.filter(
                arrangement__students=user,
                start_time__lt=self._config.server_time,
                end_time__gt=self._config.server_time
            )
            for access in access_list:
                asgn_set = access.asgn_set.all()
                for asgn in asgn_set:
                    if not asgn_list.__contains__(asgn):
                        asgn_list.append(asgn)

        self._template_file = "account/space/user_detail.html"
        self._context = {
            'account': user,
            'problem_visiteds': user.problemvisited_set.all(),
            'asgn_list': asgn_list,
            'asgn_list_count': len(asgn_list),
            'require_change_pwd': require_change_pwd,
        }

    def user_modify(self):
        """
        编辑用户
        :param user_id:
        :return:
        """
        if not self._check_login(True, True):
            self._context = "请先登录"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        if self._user_session.user_id == 'guest':
            self._context = "游客账号不支持修改信息"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        user = self._user_session.entity

        self._template_file = "account/space/user_modify.html"
        self._context = {
             "lang_provider": kernel.const.LANGUAGE_PROVIDE
        }

    def save_user_modify(self):
        """
        保存用户设置信息
        :param user_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_id == 'guest':
            self._result = kernel.RESTStruct(False, "游客账号不支持修改信息")
            return
        user = self._user_session.entity

        nickname = self._request.POST.get('nickname', '')
        email = self._request.POST.get('email', '')
        motto = self._request.POST.get('motto', '')
        old_pwd = self._request.POST.get('old_pwd', '')
        new_pwd = self._request.POST.get('new_pwd', '')
        re_pwd = self._request.POST.get('re_pwd', '')
        language = self._request.POST.get('language', '')

        if old_pwd != '':
            c1 = kernel.LoginSession.gen_passwd(old_pwd)
            c2 = user.password
            if str(c1) != str(c2):
                self._result = kernel.RESTStruct(False, u'原始密码错误，请重试！')
                return

            if str(new_pwd).strip() == "":
                self._result = kernel.RESTStruct(False, u'密码不能为空！')
                return
            if len(new_pwd) < 6:
                self._result = kernel.RESTStruct(False, u"为了你的账号安全，密码至少6位！")
                return
            if str(new_pwd) != str(re_pwd):
                self._result = kernel.RESTStruct(False, u'新密码和重复新密码不匹配！')
                return
            user.password = kernel.LoginSession.gen_passwd(new_pwd)

        if nickname.strip() == '':
            self._result = kernel.RESTStruct(False, u'昵称不能为空！')
            return
        if len(nickname) > 12:
            self._result = kernel.RESTStruct(False, u'昵称不能超过12个字符')
            return
        if email.strip() == '':
            self._result = kernel.RESTStruct(False, u'Email不能为空！')
            return
        if re.match('^\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$', email, re.I) is None:
            self._result = kernel.RESTStruct(False, u'Email格式非法！')
            return
        nns = AccountModel.User.objects.filter(nickname=nickname)
        for ns in nns:
            if ns.id != user.id:
                self._result = kernel.RESTStruct(False, u'当前昵称已经存在，请更换！')
                return
        nns = AccountModel.User.objects.filter(email=email)
        for ns in nns:
            if ns.id != user.id:
                self._result = kernel.RESTStruct(False, u'当前Email已经存在，请更换！')
                return
        if language not in kernel.const.LANGUAGE_PROVIDE:
            self._result = kernel.RESTStruct(False, u'编译语言不支持！')
            return

        if email != user.email:
            user.email_validated = False
            user.email_findpwd_validated = ''

        user.nickname = nickname
        user.email = email
        user.motto = motto
        user.preference_language = language
        user.save()

        self._result = kernel.RESTStruct(True)

    def user_avatar(self):
        """
        用户头像设置
        :param user_id:
        :return:
        """
        if not self._check_login(True, True):
            self._context = "请先登录"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        if self._user_session.user_id == 'guest':
            self._context = "游客账号不支持修改信息"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        user = self._user_session.entity

        self._template_file = "account/space/user_avatar.html"
        self._context = {

        }

    def save_user_avatar(self, user_id):
        """
        保存用户头像
        :param user_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_id == 'guest':
            self._result = kernel.RESTStruct(False, "游客账号不支持修改信息")
            return
        headimg = self._request.FILES.get('headimg')
        if headimg is None:
            self._result = kernel.RESTStruct(False, '无文件接收')
            return
        if headimg.size > 1024*1024:
            self._result = kernel.RESTStruct(False, '文件过大')
            return
        type = headimg.content_type
        ext = None
        if (type == "image/pjpeg") or (type == "image/jpeg"):
            ext = '.jpg'
        elif (type == "image/png") or (type == "image/x-png"):
            ext = '.png'
        if ext is None:
            self._result = kernel.RESTStruct(False, u'文件格式不正确，只支持jpeg/png')
            return

        path = "%s%s" % (self._user_session.entity.id, ext)
        file_name = os.path.join(kernel.const.USER_HEADIMAGE_DIR, path)
        destination = open(file_name, 'wb+')
        for chunk in headimg.chunks():
            destination.write(chunk)
        destination.close()

        x = self._request.POST.get('x', 0)
        y = self._request.POST.get('y', 0)
        w = self._request.POST.get('w', 0)
        h = self._request.POST.get('h', 0)
        try:
            x = int(float(x))
            y = int(float(y))
            w = int(float(w))
            h = int(float(h))
        except:
            self._result = kernel.RESTStruct(False, u'参数错误')
            return
        if (x == 0) or (y == 0) or (w == 0) or (h == 0):
            self._result = kernel.RESTStruct(False, u'参数错误')
            return

        oim = image.open(file_name)
        im = oim.crop((x, y, x+w, y+h))
        ori_w, ori_h = im.size
        widthRatio = heightRatio = None
        dst_w = dst_h = 180
        ratio = 1
        if (ori_w and ori_w > dst_w) or (ori_h and ori_h > dst_h):
            if dst_w and ori_w > dst_w:
                widthRatio = float(dst_w) / ori_w
            if dst_h and ori_h > dst_h:
                heightRatio = float(dst_h) / ori_h

            if widthRatio and heightRatio:
                if widthRatio < heightRatio:
                    ratio = widthRatio
                else:
                    ratio = heightRatio

            if widthRatio and not heightRatio:
                ratio = widthRatio
            if heightRatio and not widthRatio:
                ratio = heightRatio

            newWidth = int(ori_w * ratio)
            newHeight = int(ori_h * ratio)
        else:
            newWidth = ori_w
            newHeight = ori_h

        im.resize((newWidth,newHeight), image.ANTIALIAS).save(file_name, quality=90)
        user = self._user_session.entity
        user.headimg = path
        user.save()
        self._result = kernel.RESTStruct(True)

    def user_wechat(self):
        """
        用户微信绑定管理
        :param user_id:
        :return:
        """
        if not self._check_login(True, True):
            self._context = "请先登录"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        if self._user_session.user_id == 'guest':
            self._context = "游客账号不支持修改信息"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        user = self._user_session.entity

        self._template_file = "account/space/user_wechat.html"
        self._context = {
            'account': user
        }

    def email_vaild(self):
        """
        邮箱验证
        :param user_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_id == 'guest':
            self._result = kernel.RESTStruct(False, "游客账号不支持修改信息")
            return

        user = self._user_session.entity

        if user.email is None or user.email.strip() == '':
            self._result = kernel.RESTStruct(False, "未填写邮箱信息", action="redirect")
            return
        if user.email_validated:
            self._result = kernel.RESTStruct(False, "当前账号邮箱已经验证")
            return

        if user.email_findpwd_validated is not None:
            vdata = user.email_findpwd_validated.split('|')
        else:
            vdata = ['V', '', 0, 0]

        if len(vdata) != 4:
            vdata = ['V', '', 0, 0]

        if (int(time.time()) - 120) <= int(vdata[2]):
            self._result = kernel.RESTStruct(False, "请耐心查收邮件。如需重新执行发送操作请等待%s秒后重试。" %  ((int(vdata[2]) + 120) - int(time.time())))
            return


        md5 = hashlib.md5()
        md5.update("%s_%s_%s" % (uuid.uuid4(), user.id, user.email))
        hash = md5.hexdigest()

        vdata[0] = 'V'
        vdata[1] = hash
        vdata[2] = int(time.time())
        vdata[3] = int(time.time()) + 7200

        user.email_findpwd_validated = "%s|%s|%s|%s" % (vdata[0], vdata[1], vdata[2], vdata[3])

        svr = smtplib.SMTP(kernel.const.EMAIL_SMTP_SERVER)
        # 设置为调试模式，就是在会话过程中会有输出信息
        if kernel.const.EMAIL_SMTP_DEBUG:
            svr.set_debuglevel(1)
        # ehlo命令，docmd方法包括了获取对方服务器返回信息，如果支持安全邮件，返回值里会有starttls提示
        svr.docmd("EHLO server")
        svr.starttls()  # <------ 这行就是新加的支持安全邮件的代码！
        # auth login 命令
        svr.docmd("AUTH LOGIN")
        # 发送用户名，是base64编码过的，用send发送的，所以要用getreply获取返回信息
        svr.send(base64.b64encode(kernel.const.EMAIL_SMTP_SENDER) + '\r\n')
        svr.getreply()
        # 发送密码
        svr.send(base64.b64encode(kernel.const.EMAIL_SMTP_AUTH_CODE) + '\r\n')
        svr.getreply()
        # mail from, 发送邮件发送者
        svr.docmd("MAIL FROM: noreply<%s>" % kernel.const.EMAIL_SMTP_SENDER)
        # rcpt to, 邮件接收者
        svr.docmd("RCPT TO: <%s>" % user.email)
        # data命令，开始发送数据
        svr.docmd("DATA")
        # 发送正文数据
        url = "https://oj.bnuz.edu.cn/account/%s/space/email/valid?user=%s&code=%s" % (user.id, user.id, vdata[1])
        svr.send(
            "from: %s\r\nto: %s\r\nsubject: WeJudge用户安全邮箱验证\r\nContent-Type: text/html\r\n\r\n请点击此链接或者复制链接到浏览器地址栏，完成邮件验证。<br /><br /><a href='%s'>%s</a><br /><br />此链接20分钟内有效。"
            %
            (
                kernel.const.EMAIL_SMTP_SENDER,
                user.email,
                url,
                url
            )
        )
        # 比如以 . 作为正文发送结束的标记
        svr.send("\r\n.\r\n")
        svr.getreply()
        # 发送结束，退出
        svr.quit()

        user.save()

        self._result = kernel.RESTStruct(True, "已向邮箱<strong>%s</strong>发送了一封邮件，请查收并点击邮件中的链接完成验证。链接20分钟内有效。" % user.email)

    def email_vaild_check(self):
        """
        邮箱验证检查连接
        :param user_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        if not self._check_login():
            return
        if self._user_session.user_id == 'guest':
            self._context = "游客账号不支持修改信息"
            return

        user = self._user_session.entity

        if user.email_findpwd_validated is not None:
            vdata = user.email_findpwd_validated.split('|')
        else:
            vdata = ['V', '', 0, 0]

        if len(vdata) != 4:
            vdata = ['V', '', 0, 0]

        if int(time.time()) > int(vdata[3]):
            self._context = "验证链接已经过期"
            return

        if vdata[1] != self._request.GET.get('code', ''):
            self._context = "验证链接无效"
            return

        user.email_validated = True
        user.email_findpwd_validated = ''
        user.save()

        self._action = kernel.const.VIEW_ACTION_REDIRECT
        self._redirect_url = '/'

    def user_wechat_refresh_headimg(self):
        """
        用户微信绑定管理——刷新头像
        :return:
        """
        if not self._check_login():
            return
        if self._user_session.user_id == 'guest':
            self._context = "游客账号不支持修改信息"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        self._action = kernel.const.VIEW_ACTION_REDIRECT
        self._redirect_url = "https://open.weixin.qq.com/connect/qrconnect?appid=wx667fa851b07ee0ae&redirect_uri=https%3A%2F%2Foj.bnuz.edu.cn%2Fwechat%2Fapi%2Foauth2%2Fcallback&response_type=code&scope=snsapi_login&state=ref_img#wechat_redirect"

    def user_wechat_unbind(self):
        """
        用户微信解除绑定
        :return:
        """
        if not self._check_login():
            return
        if self._user_session.user_id == 'guest':
            self._context = "游客账号不支持修改信息"
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        user = self._user_session.entity
        user.wc_openid = ""
        user.save()
        self._action = kernel.const.VIEW_ACTION_REDIRECT
        self._redirect_url = reverse("account_space", args=(self._user_session.user_id, )) + "#wechat"

    def change_preference_problem_detail_list(self, mode="1"):
        """
        改变问题列表的显示方式
        :param mode: 1：详细模式，0：列表模式
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if str(mode) != "1":
            mode = False
        else:
            mode = True
        self._user_session.entity.preference_problem_detail_mode = mode
        self._user_session.entity.save()
        self._result = kernel.RESTStruct(True)


    def _get_user(self, user_id):
        """
        获取用户
        :param user_id:
        :return:
        """
        account = AccountModel.User.objects.filter(id=user_id)
        if account.exists():
            return account[0]
        else:
            return None

    def __check_permission(self, user, ajax=False, no_redirect=False):
        """
        鉴权
        :param user:
        :param ajax:
        :param no_redirect:
        :return:
        """
        if not self._check_login(ajax, no_redirect):
            return False
        if user.id == self._user_session.user_id:
            return True
        else:
            if no_redirect:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "[ERROR]当前账户没有操作权限"
                return False
            if ajax:
                self._action = kernel.const.VIEW_ACTION_JSON
                self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            else:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ADMIN_PERMISSION_DENIED
            return False