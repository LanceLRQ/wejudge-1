# -*- coding: utf-8 -*-
# coding:utf-8
import re
import sys
import xml.etree.cElementTree as Et
import urllib2
import cookielib

__author__ = 'lancelrq'

reload(sys)
sys.setdefaultencoding('utf8')


class RedirctHandler(urllib2.HTTPRedirectHandler):

    def http_error_301(self, req, fp, code, msg, headers):
        pass

    def http_error_302(self, req, fp, code, msg, headers):
        pass


class ESConnector(object):

    def __init__(self):
        self.cookie = cookielib.CookieJar()
        self.login_msg = ""
        self.is_login = False
        pass

    def login_validate(self, stucode, passwd):
        """
        登录校验
        :param stucode: 学号
        :param passwd: 密码
        :return:
        """
        header = {
            'User-Agent': 'WeJudge.ESConnector/1.0',
            'Accept': 'text/html',
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = '__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%%2FwEPDwUKMTI1OTcwODc0Ng9kFgICAQ9kFgQCCA8PZBYCHgdvbmNsaWNrBQ93aW5kb3cuY2xvc2UoKTtkAg0PFgQeCWlubmVyaHRtbAUP5a%%2BG56CB5LiN5q2j56GuHgdWaXNpYmxlZ2Rk7YWMllHqV6LbwNWGxr43Cf425jw%%3D&__VIEWSTATEGENERATOR=09394A33&__PREVIOUSPAGE=P41Qx-bOUYMcrSUDsalSZQ66PXL-H_8xeQ4t7bJ3gWnYCDI-j8Z8SOoK8eM1&__EVENTVALIDATION=%%2FwEWCwL7joKJCgLs0bLrBgLs0fbZDAK%%2FwuqQDgKAqenNDQLN7c0VAveMotMNAu6ImbYPArursYYIApXa%%2FeQDAoixx8kBnW6rorZ5%%2FA8zs6L4Q7VnbZC%%2BVVQ%%3D&TextBox1=%s&TextBox2=%s&RadioButtonList1=%%E5%%AD%%A6%%E7%%94%%9F&Button4_test='
        req = urllib2.Request("http://es.bnuz.edu.cn/default2.aspx", headers=header, data=data % (stucode, passwd))
        debug_handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(debug_handler, RedirctHandler, urllib2.HTTPCookieProcessor(self.cookie))
        try:
            web = opener.open(req)
            ctx = web.read()
            if u"密码不正确" in ctx:
                self.login_msg = "密码不正确"
            elif u"5分钟" in ctx:
                self.login_msg = "因验证接口密码错误限制，请5分钟以后再试"
            else:
                self.login_msg = "登录失败"
            self.is_login = False
            return False
        except urllib2.URLError as e:
            if hasattr(e, 'code') and e.code == 302:
                if hasattr(e, 'info') and 'error' in e.info().get('Location'):
                    self.login_msg = "登录失败"
                    self.is_login = False
                    return False
                self.login_msg = ""
                self.is_login = True
                return True
            else:
                print e.read()
                self.login_msg = "未知错误"
                self.is_login = False
                return False

    def get_student_info(self):
        if not self.is_login:
            return None
        req = urllib2.Request("http://es.bnuz.edu.cn/jwgl/xsgrxx.aspx", headers = {
            'User-Agent': 'WeJudge.ESConnector/1.0',
            'Accept': 'text/html'
        })
        student_infos = {}
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        web = opener.open(req)
        data = web.read()
        # 性别
        pattern = re.compile('<span id="lbl_xb">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['gender'] = match.group(1) if match is not None else ""
        # 姓名
        pattern = re.compile('<span id="xm">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['name'] = match.group(1) if match is not None else ""
        # 姓名
        pattern = re.compile('<span id="lbl_Xmpy">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['name_pinyin'] = match.group(1) if match is not None else ""
        # 生日
        pattern = re.compile('<span id="lbl_csrq">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['birthday'] = match.group(1) if match is not None else ""
        # 家庭住址
        pattern = re.compile('<span id="lbl_jtdz">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['address'] = match.group(1) if match is not None else ""
        # 行政班级
        pattern = re.compile('<span id="lbl_xzb">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['className'] = match.group(1) if match is not None else ""
        # 学院
        pattern = re.compile('<span id="lbl_xy">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['depName'] = match.group(1) if match is not None else ""
        # 专业
        pattern = re.compile('<span id="lbl_zymc">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['enrollSpecialityName'] = match.group(1) if match is not None else ""
        # 年级
        pattern = re.compile('<span id="lbl_dqszj">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['grade'] = match.group(1) if match is not None else ""
        # 身份证号码
        pattern = re.compile('<span id="lbl_sfzh">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['id_card'] = match.group(1) if match is not None else ""
        # 毕业中学
        pattern = re.compile('<span id="lbl_byzx">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['high_school'] = match.group(1) if match is not None else ""
        # 学历层次
        pattern = re.compile('<span id="lbl_CC">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['graduate_level'] = match.group(1) if match is not None else ""
        # 民族
        pattern = re.compile('<span id="lbl_mz">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['nation'] = match.group(1) if match is not None else ""
        # 来源省份
        pattern = re.compile('<span id="lbl_lys">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['province'] = match.group(1) if match is not None else ""
        # 来源地区
        pattern = re.compile('<span id="lbl_lydq">([^<]*)</span>')
        match = pattern.search(data)
        student_infos['city'] = match.group(1) if match is not None else ""

        return student_infos

