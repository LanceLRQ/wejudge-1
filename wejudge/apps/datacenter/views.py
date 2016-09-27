# -*- coding: utf-8 -*-
# coding:utf-8
from django.shortcuts import render
import wejudge.kernel.datacenter as DataCenter


def contest_get_status_list(request, cid):
    dcview = DataCenter.ContestAPI(request)
    dcview.get_status_list(cid)
    return dcview.render()


def contest_get_code_analysis_list(request, cid):
    dcview = DataCenter.ContestAPI(request)
    dcview.get_code_analysis_list(cid)
    return dcview.render()


def contest_receive_code_check_result(request, cid, pid):
    dcview = DataCenter.ContestAPI(request)
    dcview.receive_code_check_result(cid, pid)
    return dcview.render()
