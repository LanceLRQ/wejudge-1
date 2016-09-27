# -*- coding: utf-8 -*-
# coding:utf-8

import time
import uuid
import hashlib
import const
import urllib2
import datetime

__author__ = 'lancelrq'


class GeneralTools(object):

    @staticmethod
    def friendly_time(timestamp):
        now = int(time.time())
        des = now - timestamp
        if des > 86400:
            return GeneralTools.get_full_time_str(timestamp)
        elif des >= 3600:
            des = int(des / 3600)
            return u'%d小时前' % des
        elif des >= 60:
            des = int(des / 60)
            return u'%d分钟前' % des
        else:
            return u'%d秒前' % des

    @staticmethod
    def get_full_time_str(timestamp, arg=None):
        if arg is None:
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        if str(arg) == 'date':
            return time.strftime("%Y-%m-%d", time.localtime(timestamp))
        if str(arg) == 'creater':
            d = int(time.time() / 86400) * 86400 - 8 * 3600
            t = d + int(timestamp)
            return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
        elif str(arg) == 'time':
            h = timestamp / 3600
            m = (timestamp % 3600) / 60
            s = (timestamp % 3600) % 60
            return "%02d:%02d:%02d" % (h, m, s)

    @staticmethod
    def ratio(a, b):
        try:
            if (a == 0) or (b == 0):
                return "0.00"
            return "%.2f" % (a * 100.0 / b)
        except:
            return "NaN"

    @staticmethod
    def set_cookie_item(key, value='', max_age=None, expires=None, path='/', domain=None, secure=None, httponly=False):
        return {
            "key": key,
            "value": value,
            "max_age": max_age,
            "expires": expires,
            "path": path,
            "domain": domain,
            "secure": secure,
            "httponly": httponly
        }

    @staticmethod
    def check_time_passed(start_time=0, end_time=0):
        """
        过期检查（基于时间检查方法）
        :param start_time:开始时间
        :param end_time:结束时间
        :return:
        """
        now_time = int(time.time())
        if now_time > end_time:
            return 1, now_time - end_time       # 已结束，返回已过去多少时间
        elif now_time < start_time:
            return -1, start_time - now_time    # 未开始，返回距离开始还剩
        return 0, end_time - now_time           # 运行中，返回剩余时间

    @staticmethod
    def get_my_handle_id():
        uuid1 = uuid.uuid1()
        md5 = hashlib.md5()
        md5.update(str(uuid1))
        return md5.hexdigest()[8:-8]

    @staticmethod
    def save_head_image_from_url(url, id):
        """
        将网络上的图像下载到本地
        :param url:
        :return:
        """
        try:
            curl = urllib2.urlopen(url)
            type = curl.info().get('Content-Type', '')
            fileext = 'jpg'
            if type == 'image/png':
                fileext = 'png'
            elif type == 'image/bmp':
                fileext = 'png'
            filename = "%s.%s" % (id, fileext)
            f = open('%s/%s' % (const.USER_HEADIMAGE_DIR, filename), 'wb')
            f.write(curl.read())
            f.close()
            return filename
        except Exception, ex:
            print str(ex)
            return False

    @staticmethod
    def _get_langauage_limit(parent='all', children='inherit'):
        """
        获取语言提供列表
        :param parent: 父节点允许的语言
        :param children: 子节点允许的语言
        :return:
        """
        if parent == 'inherit' or parent == 'all':
            parent = const.LANGUAGE_PROVIDE
        else:
            parent = parent.split(",")

        if children == 'inherit':
            children = parent
        else:
            children = children.split(",")

        return children

    @staticmethod
    def get_year_terms():
        """
        自动计算学期模块
        :return:
        """
        year = datetime.datetime.now().year
        month = datetime.datetime.now().month
        if month < 8:
            year -= 1
        year_terms = []
        for i in range(2014, year + 1)[::-1]:
            if i == datetime.datetime.now().year and month >= 8:
                k = 2
            else:
                k = 3
            for j in range(1, k)[::-1]:
                year_terms.append({"year": i, "term": j})

        return year_terms
