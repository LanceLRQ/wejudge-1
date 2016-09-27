# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
import wejudge.apps.contest.models as ContestModel
import wejudge.apps.account.models as AccountModel
import wejudge.kernel.problem as ProblemKernel
import wejudge.apps.problem.models as ProblemModel
import wejudge.apps.datacenter.models as DCModel
import ContestProvider as CP
import json
import os
import time
import datetime
import uuid
import xlrd

__author__ = 'lancelrq'


class ContestBody(CP.ContestProvider, ProblemKernel.ProblemBody, ProblemKernel.JudgeStatus):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'contest'

    def contest_body(self, contest_id):
        """
        比赛首页
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        self._template_file = "contest/body/index.html"
        self._context = {
            "is_referee": self._check_admin_permission(contest),
            "contest": contest,
            'type': "index",
            'faqs': ContestModel.FAQ.objects.filter(contest=contest, is_private=False).order_by("-id")
        }

    def problems_list(self, contest_id):
        """
        比赛问题列表
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        cproblem_list = contest.problemset.order_by('index').all()
        problem_list = []
        contest_problem_list = {}
        contest_problem_counter = {}
        user_solution_counter = {}
        user_solution_is_finish = {}
        for cproblem in cproblem_list:
            pid = cproblem.problem.id
            problem_list.append(cproblem.problem)
            contest_problem_list[pid] = cproblem
            contest_problem_counter[pid] = {
                'total': cproblem.submission,
                'ac': cproblem.accepted,
                'ratio': kernel.GeneralTools.ratio(cproblem.accepted, cproblem.submission)
            }
            sol = ContestModel.ContestSolution.objects.filter(contest=contest, problems=cproblem.problem, author=self._user_session.entity)
            if sol.exists():
                sol = sol[0]
                user_solution_counter[pid] = {
                    'total': sol.submission,
                    'ac': sol.accepted,
                    'ratio': kernel.GeneralTools.ratio(sol.accepted ,sol.submission)
                }
                if sol.accepted > 0:
                    user_solution_is_finish[pid] = True

        flag, desc = self._check_time_passed(contest)

        self._template_file = "contest/body/problem_list.html"
        self._context = {
            "type": "problem_list",
            "is_referee": self._check_admin_permission(contest),
            "time_permission": flag,
            "contest": contest,
            "cproblem_list": cproblem_list,
            'contest_problem_counter': contest_problem_counter,
            'user_solution_counter': user_solution_counter,
            'user_solution_is_finish': user_solution_is_finish,
        }

    def show_contest_problem(self, contest_id,problem_id):
        """
        显示问题内容
        :param contest_id:
        :param problem_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        is_referee = self._check_admin_permission(contest)
        if not is_referee:
            flag, times = self._check_time_passed(contest)
            if flag == -1:
                self._send_error_contest_not_start()
                return
            elif flag == 1:
                self._send_error_contest_ended()
                return

        cproblem = contest.problemset.filter(problem__id=problem_id)
        if not cproblem.exists():
            self._send_error_contest_problem_not_found()
            return

        if not super(ContestBody, self).show_problem(problem_id, True):            # 调用上级题目展示
            return

        language_provider = kernel.GeneralTools._get_langauage_limit(contest.lang, cproblem[0].lang)

        self._context.update({
            'contest': contest,
            "is_referee": is_referee,
            'cproblem': cproblem[0],
            'language_provider': language_provider,
        })
        self._template_file = "problem/problem/view.html"

    def contest_submit_code(self, contest_id, problem_id):
        """
        提交代码
        :param contest_id:
        :param problem_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if contest.pause:
            self._result = kernel.RESTStruct(False, '当前比赛暂停评测，请等待评测开放')
            return

        flag, times = self._check_time_passed(contest)
        if flag == -1:
            self._send_error_contest_not_start(True)
            return
        elif flag == 1:
            self._send_error_contest_ended(True)
            return

        cproblem = contest.problemset.filter(problem__id=problem_id)
        if not cproblem.exists():
            self._send_error_contest_problem_not_found(True)
            return
        cproblem = cproblem[0]

        proc_result = self._save_submission(problem_id, True)     # 调用父类设置好的方法

        if proc_result.flag is True:                        # 如果父类方法处理成功
            status = proc_result.data
            status.callback = json.dumps({'provider': 'contest', 'id': contest.id})
            status.save()
            contest.judge_status.add(status)
            contest.save()
            sol = ContestModel.ContestSolution.objects.filter(contest=contest, problems=cproblem.problem, author=self._user_session.entity)
            if not sol.exists():
                sol = ContestModel.ContestSolution()
                sol.contest = contest
                sol.problems = cproblem.problem
                sol.author = self._user_session.entity
                sol.start_time = int(time.time())
                sol.save()
            else:
                sol = sol[0]
            sol.judge_status.add(status)
            sol.submission += 1
            sol.save()
            cproblem.submission += 1
            cproblem.save()

            proc_result.data = status.id
        else:
            proc_result.data = None

        self._result = proc_result

    def contest_status(self, contest_id, page=1, limit=50):
        """
        比赛评测状态显示
        :param contest_id:
        :param page:
        :param limit:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        cproblem_list = contest.problemset.all()
        cproblem_manual_judge = []
        for cproblem in cproblem_list:
            if cproblem.judge_style > 0:
                cproblem_manual_judge.append(cproblem.problem.id)

        jst, dst = self._get_status_list(contest.judge_status)
        count = jst.count()
        pager = kernel.PagerProvider(count, limit, page, 'contest_status', 11, self._request.GET, contest.id)
        if count > 0:
            jdugestatus = jst.all()[pager.start_idx: pager.start_idx + limit]
        else:
            jdugestatus = []

        flag, desc = self._check_time_passed(contest)

        self._template_file = "contest/body/status.html"
        self._context = {
            'contest': contest,
            "time_permission": flag,
            "is_referee": self._check_admin_permission(contest),
            'cproblem_manual_judge': cproblem_manual_judge,
            'type': 'status',
            'pager': pager.render(),
            'status_list': jdugestatus
        }
        self._context.update(dst)

    def rank_list(self, contest_id):
        """
        排行榜
        :param contest_id:
        :return:
        """

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if self._user_session.is_logined():
            is_referee = self._check_admin_permission(contest)
        else:
            is_referee = False
        rank_data = self._rank_list_counter(contest, is_referee)
        try:
            rank_data = json.loads(rank_data)
        except Exception, ex:
            rank_data = {}

        hr = contest.end_time - int(time.time())

        if -3600 < hr < 3600:
            onehr_stop_flag = 1
        elif hr < -3600:
            onehr_stop_flag = 2
        else:
            onehr_stop_flag = 0

        self._template_file = "contest/body/ranklist.html"
        self._context = {
            'contest': contest,
            "is_referee": is_referee,
            'type': 'rank_list',
            'rank_data': rank_data,
            '1hr_stop_flag': onehr_stop_flag
        }

    def faq(self, contest_id):
        """
        比赛问答
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        if self._check_admin_permission(contest):
            faqs = ContestModel.FAQ.objects.filter(contest=contest).order_by("-id")
        else:
            faqs = ContestModel.FAQ.objects.filter(contest=contest, is_private=False).order_by("-id")

        my_faqs = ContestModel.FAQ.objects.filter(contest=contest, author=self._user_session.entity).order_by("-id")
        flag, desc = self._check_time_passed(contest)
        self._template_file = "contest/body/faq.html"
        self._context = {
            'contest': contest,
            "time_permission": flag,
            "is_referee": self._check_admin_permission(contest),
            'type': 'faq',
            'faqs': faqs,
            'my_faqs': my_faqs
        }

    def faq_new_msg(self, contest_id):
        """
        发起提问、公告
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        self._template_file = "contest/body/faq_editor.html"
        self._context = {
            'contest': contest,
            "is_referee": self._check_admin_permission(contest),
            'type': 'faq'
        }

    def faq_reply_msg(self, contest_id, faq_id):
        """
        裁判回复提问
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied()
            return

        if not self._check_admin_permission(contest):
            self._send_error_contest_permission_denied()
            return

        faq = ContestModel.FAQ.objects.filter(id=faq_id)
        if not faq.exists():
            self._send_error_contest_faq_not_found()
            return

        self._template_file = "contest/body/faq_editor_reply.html"
        self._context = {
            'contest': contest,
            'type': 'faq',
            'faq': faq[0]
        }

    def faq_save_new_msg(self, contest_id):
        """
        保存提问、公告
        :param contest_id:

        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        is_referee = self._check_admin_permission(contest)

        subject = self._request.POST.get("subject", "")
        content = self._request.POST.get("content", "")
        if subject.strip() == '':
            self._result = kernel.RESTStruct(False, "请输入主题")
            return
        if content.strip() == '':
            self._result = kernel.RESTStruct(False, "请输入内容")
            return

        faq = ContestModel.FAQ()
        faq.subject = subject
        faq.content = content
        faq.contest = contest
        faq.author = self._user_session.entity
        if is_referee:
            faq.is_notice = True
            faq.is_private = False
        faq.create_time = int(time.time())
        faq.save()
        self._result = kernel.RESTStruct(True)

    def faq_save_reply(self, contest_id, faq_id):
        """
        保存回复问答
        :param contest_id:

        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if not self._check_admin_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        faq = ContestModel.FAQ.objects.filter(id=faq_id)
        if not faq.exists():
            self._send_error_contest_faq_not_found(True)
            return
        faq = faq[0]

        content = self._request.POST.get("content", "")
        is_public = self._request.POST.get("is_public", "")
        if content.strip() == '':
            self._result = kernel.RESTStruct(False, "请输入回复的内容")
            return
        if is_public == '1':
            is_public = True
        else:
            is_public = False

        faq.answer_content = content
        faq.answer_referee = self._user_session.entity
        faq.answer_time = int(time.time())
        faq.is_private = not is_public
        faq.save()

        self._result = kernel.RESTStruct(True)

    def faq_del(self, contest_id):
        """
        删除提问、公告
        :param contest_id:

        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        is_referee = self._check_admin_permission(contest)
        faq_id = self._request.GET.get('id', '')
        try:
            faq_id = int(faq_id)
        except:
            return

        faq = ContestModel.FAQ.objects.filter(id=faq_id)
        if not faq.exists():
            self._result = kernel.RESTStruct(False, "问答内容不存在")
            return
        faq = faq[0]

        if is_referee:
            faq.delete()
        else:
            if self._user_session.user_id == faq.author.id:
                if faq.answer_time != 0:
                    self._result = kernel.RESTStruct(False, "您的问题已经被回复，不能删除！")
                    return
                faq.delete()
            else:
                self._result = kernel.RESTStruct(False, "非法操作")
                return

        self._result = kernel.RESTStruct(True)

    def mgr_contest_setting(self, contest_id):
        """
        比赛服设置
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if self._user_session.user_id != contest.author.id:
            self._send_error_contest_permission_denied()
            return

        self._template_file = "contest/manager/setting.html"
        self._context = {
            'contest': contest,
            "is_referee": self._check_admin_permission(contest),
            'type': 'setting'
        }

    def mgr_save_contest_setting(self, contest_id):
        """
        保存比赛设置
        :param contest_id:

        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != contest.author.id:
            self._result = kernel.RESTStruct(False, "只有比赛发起者才能够执行该操作")
            return

        title = self._request.POST.get("title", "")
        description = self._request.POST.get("description", "")
        user_limit = self._request.POST.get("user_limit", "")
        referees = self._request.POST.get("referees", "")
        if title.strip() == '':
            self._result = kernel.RESTStruct(False, "请输入比赛标题")
            return

        pause = True if self._request.POST.get("pause_judge", "0") == '1' else False

        lang = self._request.POST.getlist("lang", "")
        if len(lang) == 0:
            self._result = kernel.RESTStruct(False, "请至少分配一种评测语言")
            return
        cnt = 0
        asgn_lang = kernel.const.LANGUAGE_PROVIDE
        for i in lang:
            if i in asgn_lang:
                cnt += 1
        if cnt == len(asgn_lang):
            lang = 'all'
        else:
            lang = ','.join(lang)

        try:
            start_time = time.mktime(datetime.datetime.strptime(self._request.POST.get("start_time"), "%Y-%m-%d %H:%M:%S").timetuple())
            end_time = time.mktime(datetime.datetime.strptime(self._request.POST.get("end_time"), "%Y-%m-%d %H:%M:%S").timetuple())
        except:
            self._result = kernel.RESTStruct(False, "时间格式错误")
            return

        contest.user_limit = user_limit
        contest.referees = referees
        contest.title = title
        contest.description = description
        contest.pause = pause
        contest.lang = lang
        contest.start_time = start_time
        contest.end_time = end_time
        contest.save()

        self._result = kernel.RESTStruct(True)

    def mgr_user(self, contest_id):
        """
        比赛用户和权限设置
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        if self._user_session.user_id != contest.author.id:
            self._send_error_contest_permission_denied()
            return

        if self._user_session.user_id == 'acm':
            users = AccountModel.User.objects.filter(id__startswith='team').order_by("create_time")
        else:
            users = []

        self._template_file = "contest/manager/user_mgr.html"
        self._context = {
            'users': users,
            'contest': contest,
            "is_referee": self._check_admin_permission(contest),
            'type': 'user_mgr'
        }

    def mgr_code_analyzer(self, contest_id, page=1, limit=100):
        """
        代码查重列表
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return

        tflag, dsc = self._check_time_passed(contest)
        if tflag < 1:
            if not self._check_admin_permission(contest):
                self._send_error_contest_permission_denied()
                return

        if tflag < 1:
            ca_list = DCModel.ContestCodeAnalysis.objects.filter(contest=contest).order_by('-levenshtein_similarity_ratio')
        else:
            ca_list = DCModel.ContestCodeAnalysis.objects.filter(contest=contest, levenshtein_similarity_ratio__gte=0.9).order_by('-levenshtein_similarity_ratio')
        count = ca_list.count()
        pager = kernel.PagerProvider(count, limit, page, 'contest_mgr_code_analyzer', 11, self._request.GET, contest.id)
        if count > 0:
            ca_list = ca_list.all()[pager.start_idx: pager.start_idx + limit]
        else:
            ca_list = []

        self._template_file = "contest/manager/code_analyzer.html"
        self._context = {
            'list': ca_list,
            'contest': contest,
            "is_referee": self._check_admin_permission(contest),
            'type': 'code_analyzer',
            'pager': pager.render()
        }

    def mgr_code_compare(self, contest_id, ca_id):
        """
        代码查重列表
        :param contest_id:
        :return:
        """
        if not self._check_login():
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists()
            return
        tflag, dsc = self._check_time_passed(contest)
        if tflag < 1:
            if not self._check_admin_permission(contest):
                self._send_error_contest_permission_denied()
                return

        ca = DCModel.ContestCodeAnalysis.objects.filter(contest=contest, id=ca_id)
        if not ca.exists():
            self._context = '没有找到指定的代码分析结果记录'
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return
        ca = ca[0]

        ls = kernel.LocalStorage(kernel.const.USER_UPLOADCODE_DIR, '')
        code1 = ls.read_file(ca.status1.code_path)
        code2 = ls.read_file(ca.status2.code_path)

        self._template_file = "contest/manager/code_compare.html"
        self._context = {
            'code_analysis': ca,
            'code1': code1,
            'code2': code2
        }



    def mgr_add_new_problems(self, contest_id):
        """
        添加题目（按照题号）
        :param contest:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != contest.author.id:
            self._result = kernel.RESTStruct(False, "只有管理员才能够执行该操作")
            return

        problem_ids = self._request.POST.get('problem_ids', '')
        problem_ids = problem_ids.split(',')
        msg = []
        for id in problem_ids:
            if contest.problemset.filter(problem__id=id).exists():
                msg.append(id + "[存在]")
                continue
            problem = ProblemModel.Problem.objects.filter(id=id)
            if not problem.exists():
                msg.append(id + "[未找到]")
                continue
            cproblem = ContestModel.ContestProblems()
            cproblem.problem = problem[0]
            cproblem.index = contest.problemset.count() + 1
            cproblem.save()
            contest.problemset.add(cproblem)

        if len(msg) == 0:
            self._result = kernel.RESTStruct(True, '操作成功完成')
        else:
            self._result = kernel.RESTStruct(True, '操作成功完成，但以下项目出现问题：<br />' + '<br />'.join(msg))

    def mgr_remove_problems(self, contest_id):
        """
        移除题目
        :param contest_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != contest.author.id:
            self._result = kernel.RESTStruct(False, "只有管理员才能够执行该操作")
            return

        problem_ids = self._request.POST.getlist('problem_ids')
        msg = []
        for id in problem_ids:
            cproblem = contest.problemset.filter(problem__id=id)
            if not cproblem.exists():
                msg.append(id + "[不存在]")
            else:
                cproblem = cproblem[0]
                contest.problemset.remove(cproblem)
                cproblem.delete()
                msg.append(id + "(%s)" % cproblem.index + "[移除成功]")

        self._result = kernel.RESTStruct(True, '操作成功完成<br />' + '<br />'.join(msg))

    def mgr_modify_problem_setting(self, contest_id, problem_id):
        """
        题目设置
        :param contest_id:
        :param problem_id:
        :return:
        """

        if not self._check_login(True, True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return

        if not self._check_permission(contest):
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return

        if self._user_session.user_id != contest.author.id:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "只有比赛发起者才能够执行该操作"
            return

        cproblem = contest.problemset.filter(problem__id=problem_id)
        if not cproblem.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return

        self._template_file = "contest/manager/ajax_problem_setting.html"
        self._context = {
            "cproblem": cproblem[0],
            "contest": contest
        }

    def mgr_save_problem_setting(self, contest_id, problem_id):
        """
        保存题目设置
        :param contest_id:
        :param problem_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != contest.author.id:
            self._result = kernel.RESTStruct(False, "只有比赛发起者才能够执行该操作")
            return

        cproblem = contest.problemset.filter(problem__id=problem_id)
        if not cproblem.exists():
            self._send_error_contest_problem_not_found(True)
            return
        cproblem = cproblem[0]

        judge_style = self._request.POST.get("judge_style", "0")
        if not str.isdigit(str(judge_style)):
            judge_style = 0
        judge_style = int(judge_style)

        lang = self._request.POST.getlist("lang")
        if len(lang) == 0:
            self._result = kernel.RESTStruct(False, "请至少分配一种评测语言")
            return
        cnt = 0
        clang = contest.lang.split(",") if contest.lang != 'all' else kernel.const.LANGUAGE_PROVIDE
        for i in lang:
            if i not in clang:
                cnt += 1
        if cnt == 0 and (len(lang) == len(clang)):
            lang = 'inherit'
        else:
            lang = ','.join(lang)

        cproblem.judge_style = judge_style
        cproblem.lang = lang
        cproblem.save()

        self._result = kernel.RESTStruct(True)

    def mgr_start_problem_rejudge(self, contest_id, problem_id):
        """
        启动重判队列
        :param contest_id:
        :param problem_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != contest.author.id:
            self._result = kernel.RESTStruct(False, "只有比赛发起者才能够执行该操作")
            return

        cproblem = contest.problemset.filter(problem__id=problem_id)
        if not cproblem.exists():
            self._send_error_contest_problem_not_found(True)
            return
        cproblem = cproblem[0]

        cstatus = contest.judge_status.filter(problem=cproblem.problem)
        for status in cstatus:
            status.flag = 9
            status.save()
            jq = ProblemModel.JudgeQueue()
            jq.judge_status = status
            jq.queue_status = -1
            jq.save()

        self._result = kernel.RESTStruct(True)

    def mgr_change_status(self, contest_id, status_id):
        """
        更改评测状态
        :param contest_id:
        :param status_id:
        :return:
        """
        if not self._check_login(True, True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return

        if not self._check_permission(contest):
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            return

        cstatus = contest.judge_status.filter(id=status_id)
        if not cstatus.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[Not Found]"
            return
        cstatus = cstatus[0]

        cproblem = contest.problemset.filter(problem=cstatus.problem)
        if not cproblem.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[Not Found]"
            return
        cproblem = cproblem[0]

        if cproblem.judge_style not in [1, 2]:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "由于当前题目设置为【自动评测】，不能使用此功能"
            return

        self._template_file = "contest/manager/change_status.html"
        self._context = {
            "status": cstatus,
            "contest": contest
        }

    def mgr_save_status_change(self, contest_id, status_id):
        """
        保存题目设置
        :param contest_id:
        :param problem_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        cstatus = contest.judge_status.filter(id=status_id)
        if not cstatus.exists():
            self._result = kernel.RESTStruct(False, '没有找到相关评测记录')
            return
        cstatus = cstatus[0]

        cproblem = contest.problemset.filter(problem=cstatus.problem)
        if not cproblem.exists():
            self._send_error_contest_problem_not_found(True)
            return
        cproblem = cproblem[0]

        if cproblem.judge_style not in [1, 2]:
            self._result = kernel.RESTStruct(False, '由于当前题目设置为【自动评测】，不能使用此功能')
            return

        flag = self._request.POST.get('flag', -1)

        try:
            flag = int(flag)
        except:
            flag = -1

        if flag < 0 or flag > 8:
            self._result = kernel.RESTStruct(False, '参数错误')
            return

        cstatus.flag = flag
        cstatus.save()
        jsapi = ProblemKernel.JudgeServiceAPI(self._request)
        jsapi.status_callback_proc(cstatus)
        self._result = kernel.RESTStruct(True)

    def read_xls_to_change_team_user_info(self, contest_id):
        """
        比赛专用账号信息导入
        :param contest_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != 'acm':
            self._result = kernel.RESTStruct(False, "只有ACM协会专用账号才能够执行该操作")
            return

        files = self._request.FILES.get('upload_xls')
        if files is None:
            self._result = kernel.RESTStruct(False, "没有找到上传的文件")
            return

        path = "contest_xls/%s%s" % (uuid.uuid4(), '.xls')
        file_name = os.path.join(kernel.const.IMPORT_PROCESS_TEMP_DIR, path)
        destination = open(file_name, 'wb+')
        for chunk in files.chunks():
            destination.write(chunk)
        destination.close()
        try:
            xls_sheet = xlrd.open_workbook(file_name)
            xls_table = xls_sheet.sheet_by_index(0)
            for i in range(2, xls_table.nrows):
                user_row = xls_table.row_values(i)
                team_id = user_row[0]
                if team_id[0:4] != 'team':
                    continue
                team = AccountModel.User.objects.filter(id=team_id)
                if not team.exists():
                    continue
                team = team[0]
                team.nickname = user_row[1]
                team.realname = user_row[2]
                team.sex = 0 if str(user_row[3]) == 'Y' else 1
                team.password = self._user_session.gen_passwd(user_row[4])
                team.locked = False
                team.save()
            self._result = kernel.RESTStruct(True)
        except:
            self._result = kernel.RESTStruct(False, "XLS文件处理过程出现错误，请检查XLS文件是否填写正确")
            return

    def mgr_reset_user_passwd(self, contest_id):
        """
        重设专用账户的密码
        :param contest_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != 'acm':
            self._result = kernel.RESTStruct(False, "只有ACM协会专用账号才能够执行该操作")
            return

        uid = self._request.POST.get('user_id', '')
        pwd = self._request.POST.get('pwd', '')

        if uid.strip() == '' or uid[0:4] != 'team':
            self._result = kernel.RESTStruct(False, "仅支持修改比赛专用账户的密码")
            return

        if pwd.strip() == '':
           pwd = "123456"

        team = AccountModel.User.objects.filter(id=uid)
        if not team.exists():
            self._result = kernel.RESTStruct(False, "未找到比赛专用账户")
            return
        team = team[0]
        team.password = self._user_session.gen_passwd(pwd)
        team.save()
        self._result = kernel.RESTStruct(True)

    def mgr_lock_contest_user(self, contest_id):
        """
        锁定/解锁专用账户
        :param contest_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        contest = self._get_contest(contest_id)
        if contest is None:
            self._send_error_contest_doesnt_exists(True)
            return

        if not self._check_permission(contest):
            self._send_error_contest_permission_denied(True)
            return

        if self._user_session.user_id != 'acm':
            self._result = kernel.RESTStruct(False, "只有ACM协会专用账号才能够执行该操作")
            return

        action = self._request.GET.get('action', '')
        uid = self._request.GET.get('user_id', '')
        if uid.strip() == '' or uid[0:4] != 'team':
            self._result = kernel.RESTStruct(False, "仅支持修改比赛专用账户的密码")
            return

        team = AccountModel.User.objects.filter(id=uid)
        if not team.exists():
            self._result = kernel.RESTStruct(False, "未找到比赛专用账户")
            return
        team = team[0]
        team.locked = True if action == 'lock' else False
        team.save()
        self._result = kernel.RESTStruct(True)