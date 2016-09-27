# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.apps.account.models as AccountModel
import wejudge.kernel.general as kernel
import re
import time
import json
import hashlib
import uuid
import sys
import smtplib
import os
import base64
__author__ = 'lancelrq'


class Account(kernel.ViewerFramework):
    """用户账户提供类"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'account'

    def login(self):
        """
        登录页面（过时）
        :return:
        """
        if self._user_session.is_logined():
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = '/'
        else:
            self._template_file = "account/login.html"
            if "/account/register" in self._request.GET.get("referer", '/'):
                self._context = {
                    "referer": "/"
                }
            else:
                self._context = {
                    "referer": self._request.GET.get('referer', '/')
                }

    def login_out(self):
        """
        登出页面
        :return:
        """
        cookie = self._user_session.logout()
        self.add_cookie(cookie)
        self._action = kernel.const.VIEW_ACTION_REDIRECT
        self._redirect_url = '/'

    def login_ajax(self):
        """
        登录页面(ajax)
        :return:
        """
        self._template_file = "account/login_ajax.html"

    def check_login(self):
        self._action = kernel.const.VIEW_ACTION_JSON
        user = self._request.POST.get('user')
        password = self._request.POST.get('password')
        referer = self._request.POST.get('referer', '/')
        rememberme = self._request.POST.get('rememberme', '')

        if not self._config.web_pwd_equal_username:
            if str(user) == str(password):
                self._result = kernel.RESTStruct(False, -4, data=referer)
                return

        if self._config.web_login_limit and (user != 'admin'):
            if (self._config.web_login_black_list is not None) and (self._config.web_login_black_list.strip() != ""):
                black_list = str(self._config.web_login_black_list).split("\n")
            else:
                black_list = []
            if (self._config.web_login_white_list is not None) and (self._config.web_login_white_list.strip() != ""):
                white_list = str(self._config.web_login_white_list).split("\n")
            else:
                white_list = []
            # 黑名单处理
            for item in black_list:
                if re.match(item.strip(), user) is not None:
                    self._result = kernel.RESTStruct(False, -6, data=referer)
                    return
            flag = True if len(white_list) == 0 else False
            # 白名单处理
            for item in white_list:
                if re.match(item.strip(), user) is not None:
                    flag = True
                    break
            if not flag:
                self._result = kernel.RESTStruct(False, -6, data=referer)
                return

        flag, errcode = self._user_session.login(user, password)
        self._result = kernel.RESTStruct(flag, errcode, data=referer)
        if flag and str(rememberme) == '1':
            cookie = self._user_session.create_login_cookie()
            self.add_cookie(cookie)

    def register(self):
        """
        用户注册（过时）
        :return:
        """
        if self._user_session.is_logined():
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = '/'
        else:
            self._template_file = "account/register.html"
            self._context = {

            }

    def save_register_student(self):
        """
        验证教务密码
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        username = self._request.POST.get('user', "")
        jw_pwd = self._request.POST.get('password', "")

        if username.strip() == '':
            self._result = kernel.RESTStruct(False, "学号不能为空！")
            return
        username_vaild = re.compile("^(\d{10})$")
        if username_vaild.match(username) is None:
            self._result = kernel.RESTStruct(False, '学号不符合规范！')
            return
        nns = AccountModel.User.objects.filter(id=username)
        if nns.exists():
            self._result = kernel.RESTStruct(False, '当前用户已存在！')
            return
        esc = kernel.ESConnector()
        if not esc.login_validate(username, jw_pwd):
            self._result = kernel.RESTStruct(False, "教务系统认证失败！接口返回信息：" + esc.login_msg)
            return
        else:
            info = esc.get_student_info()
            user = AccountModel.User()
            user.id = username
            user.password = kernel.LoginSession.gen_passwd(jw_pwd)
            user.realname = info.get('name')
            user.nickname = info.get('name')
            user.role = 1
            user.create_time = int(time.time())
            if str(info.get('gender')) == '男':
                user.sex = 1
            else:
                user.sex = 0
            user.save()

            stu = AccountModel.Student()
            stu.account = user
            stu.studentId = username
            stu.studentPwd = jw_pwd
            stu.studentName = info.get('name')
            stu.grade = info.get('grade')
            stu.sex = info.get('gender')
            stu.className = info.get('className')
            stu.department = info.get('depName')
            stu.major = info.get('enrollSpecialityName')
            stu.rawData = json.dumps(info)
            stu.save()

            self._result = kernel.RESTStruct(True)

    def save_register(self):
        """
        保存用户注册信息
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._config.web_register:
            self._result = kernel.RESTStruct(False, '系统未开放普通用户注册。')
            return
        username = self._request.POST.get('username', "").strip()
        password = self._request.POST.get('password', "").strip()
        repassword = self._request.POST.get('repassword', "").strip()
        nickname = self._request.POST.get('nickname', "").strip()
        email = self._request.POST.get('email', "").strip()

        if username == '':
            self._result = kernel.RESTStruct(False, "用户名不能为空！")
            return
        username_vaild = re.compile("^[_a-zA-Z0-9]{3,12}$")
        if username_vaild.match(username) is None:
            self._result = kernel.RESTStruct(False, '用户名不符合规范，请检查是否存在中文、标点符号，以及长度是否在3-12个字符。')
            return
        nns = AccountModel.User.objects.filter(id=username)
        if nns.exists():
            self._result = kernel.RESTStruct(False, '当前用户已存在！')
            return
        if password == '':
            self._result = kernel.RESTStruct(False, "请输入用户密码！")
            return
        if password != repassword:
            self._result = kernel.RESTStruct(False, "用户密码和重复密码不匹配，请重新输入！")
            return
        if len(password) < 6:
            self._result = kernel.RESTStruct(False, "密码太短，不安全！")
            return
        if len(password) > 20:
            self._result = kernel.RESTStruct(False, "密码太长了，怕你记不住！")
            return
        do_not_use_this_pwd = [
            username, nickname, email
        ]
        if password in do_not_use_this_pwd:
            self._result = kernel.RESTStruct(False, "密码内容太简单了，不安全！")
            return
        nickname_vaild = re.compile(u'^[\u4e00-\u9fa5_a-zA-Z0-9]{1,12}$')
        if nickname_vaild.match(nickname) is None:
            self._result = kernel.RESTStruct(False, "昵称不符合规范，请检查是否存在非法字符和标点符号，以及长度是否为1-12个字符！")
            return

        if AccountModel.User.objects.filter(nickname=nickname).exists():
            self._result = kernel.RESTStruct(False, '当前昵称已经存在，请更换！')
            return

        email_vaild = re.compile("^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]{2,})+$", re.I)
        if email_vaild.match(email) is None:
            self._result = kernel.RESTStruct(False, "邮箱地址不合法！")
            return
        user = AccountModel.User()
        user.id = username
        user.password = kernel.LoginSession.gen_passwd(password)
        user.realname = ''
        user.email = email
        user.nickname = nickname
        user.role = 0   # 普通用户
        user.create_time = int(time.time())
        user.save()

        self._result = kernel.RESTStruct(True)

    def find_pwd_start(self):
        """
        开始找回邮件
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        user_id = self._request.GET.get('user', '')
        if user_id.strip() == '':
            self._result = kernel.RESTStruct(False, "未知账号")
            return
        if user_id == 'guest':
            self._result = kernel.RESTStruct(False, "游客账号不支持修改信息")
            return
        user = AccountModel.User.objects.filter(id=user_id)
        if not user.exists():
            self._result = kernel.RESTStruct(False, "该账号不存在")
            return
        user = user[0]
        if user.email is None or user.email.strip() == '' or user.email_validated is False:
            self._result = kernel.RESTStruct(False, "该账号未绑定过邮箱或者未通过邮箱验证，无法进行找回密码的操作！")
            return

        if user.email_findpwd_validated is not None:
            vdata = user.email_findpwd_validated.split('|')
        else:
            vdata = ['F', '', 0, 0]

        if len(vdata) != 4:
            vdata = ['F', '', 0, 0]

        if (int(time.time()) - 120) <= int(vdata[2]):
            self._result = kernel.RESTStruct(False, "请耐心查收邮件。如需重新执行发送操作请等待%s秒后重试。" %  ((int(vdata[2]) + 120) - int(time.time())))
            return

        md5 = hashlib.md5()
        md5.update("%s_%s_%s" % (uuid.uuid4(), user.id, user.email))
        hash = md5.hexdigest()

        vdata[0] = 'F'
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
        url = "https://oj.bnuz.edu.cn/account/findpwd/valid?user=%s&code=%s" % (user.id, vdata[1])
        svr.send(
            "from: %s\r\nto: %s\r\nsubject: WeJudge找回密码\r\nContent-Type: text/html\r\n\r\n请点击此链接或者复制链接到浏览器地址栏，完成找回密码的操作。<br /><br /><a href='%s'>%s</a><br /><br />此链接20分钟内有效。<strong>如果不是您本人的操作，请忽略！</strong>"
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

        self._result = kernel.RESTStruct(True, "已向邮箱<strong>%s</strong>发送了一封邮件，请查收并点击邮件中的链接完成后续操作。链接20分钟内有效。" % user.email)

    def find_pwd_final(self):

        self._action = kernel.const.VIEW_ACTION_DEFAULT

        user_id = self._request.GET.get('user', '')
        code = self._request.GET.get('code', '')

        if user_id.strip() == '':
            return
        if user_id in ['guest', 'admin']:
            self._context = "账号不存在"
            return

        user = AccountModel.User.objects.filter(id=user_id)
        if not user.exists():
            self._context = "账号不存在"
            return
        user = user[0]

        if user.email_findpwd_validated is not None:
            vdata = user.email_findpwd_validated.split('|')
        else:
            vdata = ['F', '', 0, 0]

        if len(vdata) != 4:
            vdata = ['F', '', 0, 0]

        if vdata[0] != 'F':
            self._context = "异常操作"
            return

        if int(time.time()) > int(vdata[3]):
            self._context = "验证链接已经过期"
            return

        if vdata[1] != self._request.GET.get('code', ''):
            self._context = "验证链接无效"
            return

        user.password = self._user_session.gen_passwd("123456")
        user.email_findpwd_validated = ''
        user.save()

        self._context = "已将账号(%s)的密码重置为123456，请登录后立即修改密码。<a href='/'>登录</a>" % user.id
