# -*- coding: utf-8 -*-
# coding:utf-8
import os
import wejudge.kernel.general as kernel
import django.core.urlresolvers

__author__ = 'lancelrq'


class Helper(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = "helper"

    def index(self):
        self._template_file = "helper/index.html"
        self._context = {
            'helper_action': 'index'
        }

    def StudentGuide(self):
        self._template_file = "helper/student_guide.html"
        self._context = {
            'helper_action': 'student_guide'
        }

    def StudentGuideViewer(self, vindex):
        self._template_file = "helper/student_guide/%s.html" % vindex

