# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.bnuzoj as BnuzOJViewer
from django.shortcuts import HttpResponse
import time
__author__ = 'lancelrq'


# BnuzOJ主站入口文件
# =====索引=====
# index - 首页
# faq - FAQ页面
# =============


def index(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.index()
    return view_body.render()


def faq(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.faq()
    return view_body.render()


def ckeditor_imgupload(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.ckeditor_imgupload()
    return view_body.render()


# ===============


def wcapi_oauth2callback(request):
    view_body = BnuzOJViewer.WeChatAPI(request)
    view_body.oauth2_callback()
    return view_body.render()


# === No Use ===
"""
def gen_pwd(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.gen_pwd()
    return view_body.render()


def fix_asgn_report(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.fix_asgn_report()
    return view_body.render()

def create_contest_account(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.create_contest_account()
    return view_body.render()

def refresh_account_sex(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.refresh_account_sex()
    return view_body.render()

def refresh_account_realname(request):
    view_body = BnuzOJViewer.BnuzOJIndex(request)
    view_body.refresh_account_realname()
    return view_body.render()

"""