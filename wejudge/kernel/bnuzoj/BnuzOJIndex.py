# -*- coding: utf-8 -*-
# coding:utf-8

import os
import uuid
import re
from PIL import Image as image
import wejudge.kernel.general as kernel
import wejudge.apps.account.models as AccountModel
import django.core.urlresolvers

__author__ = 'lancelrq'


class BnuzOJIndex(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)

    def index(self):
        if self._user_session.is_logined():
            self._action = kernel.const.VIEW_ACTION_REDIRECT
            self._redirect_url = django.core.urlresolvers.reverse("account_space", args=[self._user_session.user_id])
            return
        else:
            self._template_file = "index.html"
            self._context = {
                "referer": self._request.GET.get('referer', '/')
            }

    def ckeditor_imgupload(self):
        """
        CKEditor 图片上传接口
        :return:
        """
        callback = self._request.GET.get('CKEditorFuncNum')

        self._action = kernel.const.VIEW_ACTION_DEFAULT
        if not self._check_login(True, True):
            self._context = "<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction(%s,'', '请先登录');</script>" % callback
            return

        files = self._request.FILES.get('upload')
        if files is None:
            self._context = "<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction(%s,'', '无文件上传');</script>" % callback
            return

        if files.size > 5*1024*1024:
            self._context = "<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction(%s,'', '文件过大(5MB内)');</script>" % callback
            return
        type = files.content_type
        ext = None
        if (type == "image/pjpeg") or (type == "image/jpeg"):
            ext = '.jpg'
        elif (type == "image/png") or (type == "image/x-png"):
            ext = '.png'
        elif type == "image/gif":
            ext = '.gif'
        elif type == 'image/bmp':
            ext = 'bmp'

        if ext is None:
            self._context = "<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction(%s,'', '文件格式不正确（必须为.jpg/.gif/.bmp/.png文件）');</script>" % callback
            return

        path = "%s%s" % (uuid.uuid4(), ext)
        file_name = os.path.join(kernel.const.CKEDITOR_UPLOAD_IMAGE_DIR, path)
        destination = open(file_name, 'wb+')
        for chunk in files.chunks():
            destination.write(chunk)
        destination.close()

        self._resize_img(ori_img=file_name, dst_img=file_name, dst_w=1280, dst_h=1280, save_q=80)

        self._context = "<script type=\"text/javascript\">window.parent.CKEDITOR.tools.callFunction(%s,'%s', '');</script>" % (callback, "/resource/imgupload/" + path)

    # 等比例压缩图片
    def _resize_img(self, **args):
        args_key = {'ori_img':'','dst_img':'','dst_w':'','dst_h':'','save_q': 80}
        arg = {}
        for key in args_key:
            if key in args:
                arg[key] = args[key]

        im = image.open(arg['ori_img'])
        ori_w, ori_h = im.size
        widthRatio = heightRatio = None
        ratio = 1
        if (ori_w and ori_w > arg['dst_w']) or (ori_h and ori_h > arg['dst_h']):
            if arg['dst_w'] and ori_w > arg['dst_w']:
                widthRatio = float(arg['dst_w']) / ori_w #正确获取小数的方式
            if arg['dst_h'] and ori_h > arg['dst_h']:
                heightRatio = float(arg['dst_h']) / ori_h

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

        im.resize((newWidth,newHeight), image.ANTIALIAS).save(arg['dst_img'],quality=arg['save_q'])

    """

    def gen_pwd(self):
        pwd = self._request.GET.get('pwd', '')
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        self._context = kernel.LoginSession.gen_passwd(pwd)
        return

    def fix_asgn_report(self):

        # 修正asgn的report不准确问题

        asgns = AsgnModel.Asgn.objects.all()
        for asgn in asgns:
            reports = AsgnModel.StuReport.objects.filter(asgn=asgn)
            full_score = asgn.full_score
            asgn_problems = asgn.problemset.all()
            for report in reports:
                self.__asgn_report_count_by_solutions(asgn, report, asgn_problems)
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        self._context = "Finished."


    def refresh_account_sex(self):
        accounts = AccountModel.User.objects.all()
        for account in accounts:
            username_vaild = re.compile("^1[1-4](\d{8})$")  # 学号判断
            if username_vaild.match(account.id) is None:
                continue
            esc = kernel.ESConnector()
            info = esc.get_stu_info(account.id)
            if info is not False:
                gender = info.get('gender', '')
                if gender == u'男':
                    account.sex = 1
                elif gender == u'女':
                    account.sex = 0
                else:
                    account.sex = -1
                account.save()
                print "%s get ok. sex = %s" % (account.id, gender)

        self._action= kernel.const.VIEW_ACTION_DEFAULT
        self._context = "OK"


    def refresh_account_realname(self):
        accounts = AccountModel.User.objects.all()
        for account in accounts:
            username_vaild = re.compile("^15(\d{8})$")  # 学号判断
            if username_vaild.match(account.id) is None:
                continue
            esc = kernel.ESConnector()
            info = esc.get_stu_info(account.id)
            if info is not False:
                name = info.get('name', '')
                if name.strip() != '':
                    account.realname = name
                account.save()
                print "%s get ok. name = %s" % (account.id, name)

        self._action= kernel.const.VIEW_ACTION_DEFAULT
        self._context = "OK"
    """