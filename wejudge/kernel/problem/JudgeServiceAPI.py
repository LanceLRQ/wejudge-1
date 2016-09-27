# -*- coding: utf-8 -*-
# coding:utf-8

import time
import json
import hashlib
import wejudge.kernel.general as kernel

import wejudge.apps.problem.models as ProblemMdl
import wejudge.apps.asgn.models as AsgnModel
import wejudge.apps.contest.models as ContestModel
__author__ = 'lancelrq'


class JudgeServiceAPI(kernel.ViewerFramework):
    """评测机接口模块"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'judge_status'

    def receive_judge_result(self, sid):
        """
        接收评测结果（基础：转移result文件、核对信息等）
        :param sid: JudgeStatus ID
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._license_check():
            return
        result = self._request.POST.get("result")
        root = json.loads(result)
        status = ProblemMdl.JudgeStatus.objects.filter(id=sid)
        if status.exists():
            status = status[0]
            status.result = result
            status.flag = root.get('exitcode', 8)
            status.exe_mem = root.get('memused', 0)
            status.exe_time = root.get('timeused', 0)
            status.save()
            self.status_callback_proc(status)
            self._exchange_progrem_run_outdata(status, root.get('session_id'), root.get("outdatas"))
            self._arrange_judge_result(status)
            self._result = kernel.RESTStruct(True, data=True)

        else:
            self._result = kernel.RESTStruct(False, msg="Error: No status found.")

    def tdmaker_receive_judge_result(self, id):
        """
        [TDMaker]接收评测结果（写入全新的测试数据）
        :param sid: JudgeStatus ID
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._license_check():
            return
        result = self._request.POST.get("result")
        root = json.loads(result)
        tdq = ProblemMdl.TdmakerQueue.objects.filter(id=id)
        if tdq.exists():
            tdq = tdq[0]
            tdq.flag = root.get('exitcode', 8)
            tdq.memused = root.get('memused', 0)
            tdq.timeused = root.get('timeused', 0)
            tdq.save()
            session_id = root.get('session_id', '0')
            out_tmp_dir = kernel.LocalStorage(kernel.const.PROGRAM_RUN_OUTDATAS_TEMP, session_id)
            out_target_dir = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(tdq.problem.id))
            testdata = tdq.problem.test_data.all()
            for td in testdata:
                handle = td.handle
                out_target_dir.clone_file("%s.out" % handle, out_tmp_dir.get_file_path("%s.outdata" % handle))
            out_tmp_dir.delete('')     # 删除当前目录
            self._result = kernel.RESTStruct(True, data=True)
        else:
            self._result = kernel.RESTStruct(False, msg="Error: No tdmaker status found.")

    def tdmaker_get_problem_judge_options(self, id):
        """
        [TDMaker]获取题目评测信息（包括测试数据集合）
        :param sid: Status的ID
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._license_check():
            return
        tdq = ProblemMdl.TdmakerQueue.objects.filter(id=id)
        if not tdq.exists():
            self._result = kernel.RESTStruct(False, msg="Error: No TDmaker status found.")
            return
        tdq = tdq[0]
        problem = tdq.problem
        demo_code = {}
        if problem.demo_code is not None and problem.demo_code.strip() != "":
            demo_code = json.loads(problem.demo_code)
        lang = demo_code.get('lang', 'gcc')

        content = demo_code.get("content", "")
        tds = []
        testdatas = problem.test_data.order_by("order")
        for td in testdatas:
            tds.append(td.dump_for_judge())
        if str(lang) == 'java':
            code_path = "Main.java"
            time_limit = problem.java_time_limit
            mem_limit = problem.java_memory_limit
        else:
            code_path = "m.%s" % kernel.const.SOURCE_CODE_EXTENSION.get(lang, "c")
            time_limit = problem.c_time_limit
            mem_limit = problem.c_memory_limit

        self._result = kernel.RESTStruct(True, data={
            'lang': lang,
            'problem_id': problem.id,
            'time_limit': time_limit,
            'memory_limit': mem_limit,
            'test_data': tds,
            'code_path': code_path,
            'demo_code': content
        })

    def get_problem_judge_options(self, sid):
        """
        获取题目评测信息（包括测试数据集合）
        :param sid: Status的ID
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._license_check():
            return
        status = ProblemMdl.JudgeStatus.objects.filter(id=sid)
        if not status.exists():
            self._result = kernel.RESTStruct(False, msg="Error: No status found.")
            return
        status = status[0]
        lang = status.lang
        problem = status.problem
        tds = []
        testdatas = problem.test_data.order_by("order")
        for td in testdatas:
            tds.append(td.dump_for_judge())
        if str(lang) == 'java':
            time_limit = problem.java_time_limit
            mem_limit = problem.java_memory_limit
        else:
            time_limit = problem.c_time_limit
            mem_limit = problem.c_memory_limit

        self._result = kernel.RESTStruct(True, data={
            'lang': status.lang,
            'problem_id': problem.id,
            'status_id': status.id,
            'time_limit': time_limit,
            'memory_limit': mem_limit,
            'test_data': tds,
            'code_path': status.code_path
        })

    def _exchange_progrem_run_outdata(self, status, session_id, outdatas):
        """
        将程序输出结果复制到永久存储文件夹
        :param status:
        :param outdatas:
        :return:
        """
        out_tmp_dir = kernel.LocalStorage(kernel.const.PROGRAM_RUN_OUTDATAS_TEMP, session_id)
        out_target_dir = kernel.LocalStorage(kernel.const.PROGRAM_RUN_OUTDATAS, str(status.id))
        if outdatas is not None:
            for key, val in outdatas.iteritems():
                out_target_dir.clone_file(val, out_tmp_dir.get_file_path(val))
        out_tmp_dir.delete('')     # 删除当前目录

    def _arrange_judge_result(self, status):
        """
        处理评测结果（处理用户题目访问记录，全局统计，Asgn模块分记等事项）
        :param status: 评测状态记录
        :return:status
        """
        # 生成用户个人的评测统计
        tmp = ProblemMdl.JudgeStatus.objects.filter(problem=status.problem, author=status.author)
        total = tmp.count()
        ac = tmp.filter(flag=0).count()
        # 写入
        pv = ProblemMdl.ProblemVisited.objects.filter(problem=status.problem, author=status.author)
        if pv.exists():
            pv = pv[0]
        else:
            pv = ProblemMdl.ProblemVisited()
            pv.problem = status.problem
            pv.author = status.author
        pv.submissions = total
        pv.accepted = ac
        pv.save()
        # 个人信息统计
        author = status.author
        pv_set = author.problemvisited_set
        count = ProblemMdl.JudgeStatus.objects.filter(author=author).count()
        if int(author.submissions) != int(count):
            author.submissions = int(count)
            author.accepted = ProblemMdl.JudgeStatus.objects.filter(author=author, flag=0).count()
            author.visited = pv_set.count()
            author.solved = pv_set.filter(accepted__gt=0).count()
            author.point_solved = author.solved * 2
            author.save()
        # 全局统计
        tmp = ProblemMdl.JudgeStatus.objects.filter(problem=status.problem)
        status.problem.total = tmp.count()
        status.problem.ac = tmp.filter(flag=0).count()
        status.problem.save()
        return status.problem.total, status.problem.ac

    def status_callback_proc(self, status):
        """
        评测结果额外内容处理程序
        :param status:
        :return:
        """
        try:
            callback = json.loads(status.callback)
        except:
            return

        if callback.get('provider', '') == 'asgn':
            asgn_id = callback.get('id')
            asgn = AsgnModel.Asgn.objects.filter(id=asgn_id)
            if asgn.exists():
                asgn = asgn[0]
                sol = AsgnModel.Solution.objects.filter(asgn=asgn, problems=status.problem, author=status.author)
                if sol.exists():
                    sol = sol[0]
                    sol_status = sol.judge_status.order_by('timestamp')
                    sub = 0
                    ac = 0
                    for st in sol_status:
                        sub += 1
                        if st.flag == 0:
                            ac += 1
                            sol.first_ac_time = st.timestamp
                            break
                    sol.submission = sub
                    sol.accepted = ac
                    sol.save()
                asgn_problem = asgn.problemset.filter(problem=status.problem)
                if asgn_problem.exists():
                    asgn_problem = asgn_problem[0]
                    asgn_problem.accepted = asgn.judge_status.filter(flag=0, problem__id=status.problem.id).count()
                    asgn_problem.submission = asgn.judge_status.filter(problem__id=status.problem.id).count()
                    asgn_problem.save()
                # ===== Report Counter ======
                report = AsgnModel.StuReport.objects.filter(asgn=asgn, student=status.author)
                if report.exists():
                    self.__asgn_report_count_by_solutions(asgn, report[0])

        elif callback.get('provider', '') == 'contest':
            contest_id = callback.get('id')
            contest = ContestModel.Contest.objects.filter(id=contest_id)
            if contest.exists():
                contest = contest[0]
                sol = ContestModel.ContestSolution.objects.filter(contest=contest, problems=status.problem, author=status.author)
                if sol.exists():
                    sol = sol[0]
                    sol.first_ac_time = 0
                    sol_status = sol.judge_status.order_by('timestamp')
                    sub = 0
                    ac = 0
                    for st in sol_status:
                        sub += 1
                        if st.flag == 0:
                            ac += 1
                            sol.first_ac_time = st.timestamp
                            break
                    sol.submission = sub
                    sol.accepted = ac
                    sol.save()
                cproblem = contest.problemset.filter(problem=status.problem)
                if cproblem.exists():
                    cproblem = cproblem[0]
                    cproblem.accepted = contest.judge_status.filter(flag=0, problem__id=status.problem.id).count()
                    cproblem.submission = contest.judge_status.filter(problem__id=status.problem.id).count()
                    cproblem.save()

    def get_judge_status(self, sid):
        """
        前端：动态获取评测状态
        :param sid:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        status = ProblemMdl.JudgeStatus.objects.filter(id=sid)
        if not status.exists():
            self._result = kernel.RESTStruct(False, msg="未找到评测状态")
            return
        status = status[0]

        self._result = kernel.RESTStruct(True, data={
            "flag": status.flag,                                        # 状态
            "distance": int(time.time()) - status.timestamp             # 等待时间
        })

    def __asgn_report_count_by_solutions(self, asgn, report):
        """
        实验报告自动统计程序
        :param asgn:
        :param report:
        :return:
        """
        full_score = asgn.full_score
        asgn_problems = asgn.problemset.all()
        score = 0
        ac_cnt = 0
        total_cnt = 0
        solved_cnt = 0
        for ap in asgn_problems:
            sol = asgn.solution_set.filter(problems=ap.problem, author=report.student)
            sol = sol[0] if sol.exists() else None
            ac = True if (sol is not None) and (sol.accepted > 0) else False
            score = (score + ap.score) if ac else score
            ac_cnt += sol.accepted if (sol is not None) else 0
            total_cnt += sol.submission if (sol is not None) else 0
            solved_cnt += 1 if ac else 0
        if score > full_score:
            score = full_score
        report.judge_score = score
        report.ac_counter = ac_cnt
        report.submission_counter = total_cnt
        report.solved_counter = solved_cnt
        report.modify_time = int(time.time())
        report.save()

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
            kernel.const.JUDGE_SERVICE_API_SECERT,
            str(timestamp),
            str(randstr)
        ]
        secert.sort()       # 字典序
        secert = hashlib.sha256("".join(secert)).hexdigest()
        if str(secert) == str(signature):
            return True
        return False

    def _license_check(self):
        """
        权限检查
        :return:
        """
        check_flag = self.__api_license_check(
            self._request.GET.get('timestamp', ''), self._request.GET.get('randstr', ''), self._request.GET.get('signature', '')
        )
        if check_flag is False:
            self._result = kernel.RESTStruct(False, msg="License ERROR.")
            return False
        return True