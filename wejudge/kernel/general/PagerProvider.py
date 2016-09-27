# -*- coding: utf-8 -*-
# coding:utf-8
import math
import urllib
import django.template
import django.template.loader
import django.core.urlresolvers

__author__ = 'lancelrq'


class PagerProvider(object):
    """分页计算系统"""
    """
    索引:
    total: 总记录数
    page: 当前页面
    page_count: 系统计算的页面总数
    pager_url_jumper_list: 首页尾页url
    pager_url_list: 系统计算好的页面地址
    start_idx:  系统计算用于检索的起始记录位置,比如第二页从第15条记录开始,那它的值就是15
    __pager_calculation(): 分页计算程序
    """

    def __init__(self, total=0, limit=30, page=1, target_url='', display=11, _get=None, *args):
        """
        分页系统初始化
        :param total: 记录总数
        :param limit: 每页显示记录数
        :param page: 当前第几页
        :param target_url: Djaong URL列表中定义的URL名称
        :param args: URL渲染所需参数(可选)
        :param display: 一共显示多少个页面的直接链接
        :param _get: Request GET方法的集合
        :return:
        """
        self.total = total
        if total == 0:
            return
        if _get is not None and isinstance(_get, dict):
            self.pager_query_param = urllib.urlencode(_get)
            if self.pager_query_param != '':
                self.pager_query_param = '?' + self.pager_query_param
        else:
            self.pager_query_param = ''

        if page < 1:
            self.page = 1
        else:
            self.page = page
        self.page_count = int(math.ceil(total / (limit * 1.0)))
        if page > self.page_count:
            page = self.page_count
        self.start_idx = limit * (self.page-1)
        pages = PagerProvider.__pager_calculation(self.page_count, self.page, display=11)
        self.pager_url_list = []
        _args = []
        for item in args:
            _args.append(item)
        __args1 = _args[:]
        __args1.append(1)
        __args2 = _args[:]
        __args2.append(self.page_count)
        self.pager_url_jumper_list = [
            django.core.urlresolvers.reverse(target_url, args=__args1),
            django.core.urlresolvers.reverse(target_url, args=__args2)
        ]
        for pi in pages:
            __args = _args[:]    # copy the array
            __args.append(pi)
            self.pager_url_list.append({
                'idx': pi, 'url': django.core.urlresolvers.reverse(target_url, args=__args), 'active': (pi == self.page)
            })

    @staticmethod
    def __pager_calculation(total, nowpage=1, display=11):
        """
        分页计算程序
        :param total: 记录总数
        :param nowpage: 当前第几页
        :param display: 一共显示多少个页面的直接链接
        :return:
        """
        if total <= display:
            return range(1, total+1)
        half = int(math.ceil(display / 2.0))
        if int(nowpage) < int(half):
            return range(1, display + 1)
        if int(nowpage + half > total):
            return range(total - display + 1, total + 1)
        else:
            return range(nowpage - half + 1, nowpage + half)

    def render(self):
        """
        渲染分页页面模板
        :return:
        """
        if self.total == 0:
            return ''
        context = {
            'page_count': self.page_count,
            'now_page': self.page,
            'pages_url': self.pager_url_list,
            'first_url': self.pager_url_jumper_list[0],
            'last_url': self.pager_url_jumper_list[1],
            'query_param': self.pager_query_param
        }
        temp = django.template.loader.get_template("pager.html")
        return temp.render(context)
