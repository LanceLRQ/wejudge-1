# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import time
import json
import hashlib
import wejudge.kernel.general as kernel
import wejudge.apps.contest.models as ContestModel
import wejudge.apps.problem.models as ProblemModel
import wejudge.apps.datacenter.models as DCModel
from django.db.models import Q


class ContestAPI(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._action = kernel.const.VIEW_ACTION_JSON

    def __api_license_check(self, timestamp, randstr, signature):
        """
        接口访问权限检查
        :param timestamp:   请求时间戳
        :param randstr:     随机字符串
        :param signature:   校验码
        和微信类似，首先用secert，时间戳文本和随机字符串组成一个数组，然后按字典序排序，按顺序拼接成一个字符串，进行sha256加密，
        如果加密结果和signature相同，则视为校验成功
        :return:
        """
        secert = [
            kernel.const.DATA_CENTER_API_SECERT,
            str(timestamp),
            str(randstr)
        ]
        secert.sort()       # 字典序
        secert = hashlib.sha256("".join(secert)).hexdigest()
        if str(secert) == str(signature):
            return True
        return False

    def license_check(self):
        """
        权限检查
        :return:
        """
        check_flag = self.__api_license_check(
            self._request.GET.get('timestamp', ''),
            self._request.GET.get('randstr', ''),
            self._request.GET.get('signature', '')
        )
        if check_flag is False:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, msg="License ERROR.")
            return False
        return True

    def get_status_list(self, contest_id):
        """
        获取评测状态列表
        :param contest_id:
        :return:
        """
        if not self.license_check():
            return

        timestamp = self._request.POST.get('timestamp', '')     # 自动寻找大于当前时间戳的记录
        try:
            timestamp = int(timestamp)
        except:
            timestamp = None

        contest = ContestModel.Contest.objects.filter(id=contest_id)
        if not contest.exists():
            self._result = kernel.RESTStruct(False, 'Contest Not Found.')
            return
        contest = contest[0]

        if timestamp is not None:
            status_list = contest.judge_status.filter(timestamp__gt=timestamp, flag=0).order_by('id')
        else:
            status_list = contest.judge_status.filter(flag=0).order_by('id')

        status_list_view = []
        for status in status_list:
            status_list_view.append({
                'id': status.id,
                'problem_id': status.problem.id,
                'author_id': status.author.id,
                'flag': status.flag,
                'lang': status.lang,
                'timestamp': status.timestamp,
                'exe_time': status.exe_time,
                'exe_mem': status.exe_mem,
                'code_len': status.code_len,
                'code_path': status.code_path
            })

        self._result = kernel.RESTStruct(True, data=status_list_view)
        return

    def get_code_analysis_list(self, contest_id):
        """
        获取代码查重的项目内容
        :param contest_id:
        :return:
        """
        if not self.license_check():
            return

        ca_list = DCModel.ContestCodeAnalysis.objects.filter(contest__id=contest_id)
        ca_list_view = {}
        for ca_item in ca_list:
            problem_id = ca_item.problem.id
            ca_list_item = ca_list_view.get(problem_id, {})
            key = "%s-%s" % (ca_item.status1.id, ca_item.status2.id)
            # 注意，在检索项目的时候，s1和s2属于无顺序的项目，也就是说，s1 <-> s2，
            # 因为事实上查重算法对于两个相同的文件，它的重复率的值是一样的。
            ca_list_item[key] = ca_item.levenshtein_similarity_ratio
            ca_list_view[problem_id] = ca_list_item
        self._result = kernel.RESTStruct(True, data=ca_list_view)

    def receive_code_check_result(self, contest_id, problem_id):
        """
        接收代码查重结果
        :param contest_id:
        :return:
        """
        if not self.license_check():
            return
        status1 = self._request.POST.get('status1', 0)
        status2 = self._request.POST.get('status2', 0)
        ratio = self._request.POST.get('ratio', 0)
        try:
            ratio = float(ratio)
        except:
            self._result = kernel.RESTStruct(False, 'Cannot not convert [object]ratio to float.')
            return

        contest = ContestModel.Contest.objects.filter(id=contest_id)
        if not contest.exists():
            self._result = kernel.RESTStruct(False, 'Contest Not Found.')
            return
        contest = contest[0]
        problem = ProblemModel.Problem.objects.filter(id=problem_id)
        if not problem.exists():
            self._result = kernel.RESTStruct(False, 'Problem Not Found.')
            return
        problem = problem[0]
        status1 = ProblemModel.JudgeStatus.objects.filter(id=status1)
        if not status1.exists():
            self._result = kernel.RESTStruct(False, 'Status1 Not Found.')
            return
        status1 = status1[0]
        status2 = ProblemModel.JudgeStatus.objects.filter(id=status2)
        if not status2.exists():
            self._result = kernel.RESTStruct(False, 'Status2 Not Found.')
            return
        status2 = status2[0]
        ca_item = DCModel.ContestCodeAnalysis.objects.filter(
            Q(contest=contest, problem=problem) &
            (Q(status1=status1, status2=status2) | Q(status1=status2, status2=status1))
        )
        if not ca_item.exists():
            ca_item = DCModel.ContestCodeAnalysis()
            ca_item.problem = problem
            ca_item.contest = contest
            ca_item.status1 = status1
            ca_item.status2 = status2
        else:
            ca_item = ca_item[0]

        ca_item.levenshtein_similarity_ratio = ratio
        ca_item.save()
        self._result = kernel.RESTStruct(True,data=True)
