# -*- coding: utf-8 -*-
# coding:utf-8

import time
import hashlib
import wejudge.apps.account.models
from GeneralTools import GeneralTools
from const import *
from ESConnector import ESConnector
import math
__author__ = 'lancelrq'


class LoginSession(object):
    """用户会话处理类"""

    def __init__(self, request):
        """
        初始化
        :param request: django request 对象
        :return:
        """
        self.__request = request            # HTTP请求对象
        self.__user_id = None               # 用户ID
        self.__is_logined = False           # 用户是否登录
        self.__user = None                  # 用户内容

        # 从Session获取登录信息
        if self.__load_session(request):
            # 标记登录状态
            self.__is_logined = True
        else:
            # 从Cookie获取登录信息
            if self.__load_cookies(request):
                # 标记登录状态
                self.__is_logined = True
            else:
                self.__is_logined = False

    def login(self, username, password):
        """
        登录操作
        :param username: 用户名
        :param password: 密码
        :return: 是否登录成功, 错误代码
        """

        # 判断是否无内容
        if (username == '') or (password == ''):
            return False, -3  # 用户名或密码为空

        # 载入用户信息
        user = wejudge.apps.account.models.User.objects.filter(id=username)
        if user.exists():
            user = user[0]
            if user.locked:
                return False, -5
            self.__user_id = user.id
            self.__user = user
            # 检查是否因为重复输入密码而锁定
            rel, sec = self.__check_login_retry_lock()
            if rel is False:
                return False, sec   # 锁定, 剩余时间
            # 计算密码
            remote_pwd = str(user.password)
            now_pwd = str(LoginSession.gen_passwd(password))
            # 校验密码
            if remote_pwd == now_pwd:

                if user.login_pwd_retry_counter != ACCOUNT_LOGIN_RETRY_TOTAL:
                    # 如果密码错重试次数不为重置密码重试次数
                    self.__clean_login_retry_counter()
                self.start_login(user)
                return True, 0

            else:

                # 设置密码错误计数
                self.__set_login_retry_counter()
                # 重复输入密码次数过多, 锁定
                if user.login_pwd_retry_counter <= 0:
                    rel, sec = self.__check_login_retry_lock()
                    return rel, sec     # 锁定, 剩余时间
                else:
                    return False, -1    # 密码错误

        else:
            return False, -2        # 用户不存在

    def start_login(self, user):
        """
        登录功能快速实现类
        :return:
        """
        # 写入登录会话
        self.__request.session[ACCOUNT_LOGIN_SESSION_KEY] = user.id
        # 标记登录状态
        self.__is_logined = True
        lt = user.last_login_time
        nt = int(time.time())
        if nt - lt > 86400:
            user.point_login += 1
        user.last_login_time = int(time.time())
        user.save()

    def create_login_cookie(self):
        """
        写登录记住Cookie
        :param response: django response对象
        :return:
        """
        # 生成Token
        token = LoginSession.create_login_token(self.__user.id, self.__user.password)
        # 将Token写入数据库
        self.__user.logined_token = token
        self.__user.logined_token_expire = int(time.time()) + ACCOUNT_LOGIN_EXPIRE_TIME
        self.__user.save()
        # 写Cookie(需要传入Response对象)
        cookie_resp = list()
        cookie_resp.append(GeneralTools.set_cookie_item(ACCOUNT_LOGIN_COOKIE_TOKEN, token, expires=ACCOUNT_LOGIN_EXPIRE_TIME))
        cookie_resp.append(GeneralTools.set_cookie_item(ACCOUNT_LOGIN_COOKIE_UID, self.__user.id, expires=ACCOUNT_LOGIN_EXPIRE_TIME))
        return cookie_resp

    def logout(self):
        """
        登出操作
        :param response: django response对象
        :return:
        """
        # 清除Session
        self.__request.session[ACCOUNT_LOGIN_SESSION_KEY] = None
        # 清除Token
        if self.__user is not None:
            self.__user.logined_token = ""
            self.__user.logined_token_expire = 0
            self.__user.save()
        # 清除Cookie
        cookie_resp = list()
        cookie_resp.append(GeneralTools.set_cookie_item(ACCOUNT_LOGIN_COOKIE_TOKEN, '', expires=-1))
        cookie_resp.append(GeneralTools.set_cookie_item(ACCOUNT_LOGIN_COOKIE_UID, '', expires=-1))
        return cookie_resp

    def is_logined(self):
        """判断是否已经登录"""
        return self.__is_logined

    def __getattr__(self, item):
        if str(item[0:5]) == str('user_'):      # 获取用户信息
            return self.__user.__getattribute__(item[5:])
        if str(item[0:11]) == str('preference_'):      # 获取偏好设置
            return self.__user.__getattribute__(item)
        elif str('user') == str(item):          # 获取用户信息对象
            return self.__user
        elif str('headimg') == str(item):          # 获取用户头像信息
            return "/resource/headimg/%s" % self.__user.headimg
        if str('entity') == str(item):          # 获取用户信息对象
            return self.__user
        elif str('logined') == str(item):
            return self.__is_logined
        else:
            return object.__getattribute__(self, item)

    def __load_session(self, request):
        """
        从Session里读取登录信息
        :param request:
        :return:
        """
        if ACCOUNT_LOGIN_SESSION_KEY in request.session:
            if request.session.get(ACCOUNT_LOGIN_SESSION_KEY) is None or request.session.get(ACCOUNT_LOGIN_SESSION_KEY).strip() == '':
                return False
            user_id = request.session.get(ACCOUNT_LOGIN_SESSION_KEY)
            user = wejudge.apps.account.models.User.objects.filter(id=user_id)
            if user.exists():
                user = user[0]
                if user.locked:
                    return False
                self.__user_id = user.id
                self.__user = user
                return True
            else:
                return False
        else:
            return False

    def __load_cookies(self, request):
        """
        从Cookie里读取登录信息
        :param request:
        :return:
        """
        if ACCOUNT_LOGIN_COOKIE_TOKEN in request.COOKIES:

            user_token = request.COOKIES[ACCOUNT_LOGIN_COOKIE_TOKEN]
            user_id = request.COOKIES[ACCOUNT_LOGIN_COOKIE_UID]
            account = wejudge.apps.account.models.User.objects.filter(id=user_id)
            if account.exists():
                account = account[0]
                if account.locked:
                    return False
                remote_token = account.logined_token
                expire = account.logined_token_expire
                # 判断Token是否过期
                if (remote_token is not None) and (str(remote_token) == str(user_token)) and (expire > int(time.time())):
                    # 未过期
                    self.__user_id = account.id
                    self.__user = account
                    return True
                else:
                    # 过期
                    account.logined_token = None
                    account.logined_token_expire = 0
                    account.save()
                    return False
            else:
                return False
        else:
            return False

    def __set_login_retry_counter(self):
        """
        设置密码错误重试次数
        :return:
        """
        c = self.__user.login_pwd_retry_counter - 1
        if c <= 0:
            self.__request.session[ACCOUNT_LOGIN_SESSION_RETRY_TIME] = int(time.time()) + ACCOUNT_LOGIN_RETRY_WAIT_TIME
        self.__user.login_pwd_retry_counter = c
        self.__user.save()

    def __clean_login_retry_counter(self):
        """
        清除密码错误重试次数
        :return:
        """
        self.__request.session[ACCOUNT_LOGIN_SESSION_RETRY_TIME] = int(time.time()) - 1000
        self.__user.login_pwd_retry_counter = ACCOUNT_LOGIN_RETRY_TOTAL
        self.__user.save()

    def __check_login_retry_lock(self):
        """
        检查是否锁定
        :return:
        """
        if ACCOUNT_LOGIN_SESSION_RETRY_TIME in self.__request.session:
            login_allow_time = int(self.__request.session.get(ACCOUNT_LOGIN_SESSION_RETRY_TIME))
            now = int(time.time())
            # 判断是否超出锁定时间
            if login_allow_time > now:
                p = login_allow_time - now
                return False, p
            else:
                self.__user.login_pwd_retry_counter = 5
                self.__user.save()
        return True, 0

    @staticmethod
    def gen_passwd(pwd):
        """
        密码密文生成器(静态)
        算法: sha256($salt.md5($pwd))
        :param pwd: 密码明文
        :return:
        """
        try:
            pwd = str(pwd)
            md5 = hashlib.md5()
            md5.update(pwd)
            pwd = md5.hexdigest()       # 小写
            pwd = '%s%s' % (ACCOUNT_PASSWORD_SALT, pwd)
            sha256 = hashlib.sha256()
            sha256.update(pwd)
            pwd = sha256.hexdigest()    # 小写
            return pwd

        except BaseException, e:
            return ''

    @staticmethod
    def create_login_token(username, passwd):
        """
        登录令牌生成器(静态)
        :param username: 用户名
        :param passwd: 密码
        :return:
        """

        token = '%s.%s.%s' % (username, passwd, str(time.time()))
        md5 = hashlib.md5()
        md5.update(token)
        token = md5.hexdigest()
        token = '%s%s' % (token, ACCOUNT_PASSWORD_SALT)
        sha256 = hashlib.sha256()
        sha256.update(token)
        token = sha256.hexdigest()
        return token
