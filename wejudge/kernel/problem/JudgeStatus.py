# -*- coding: utf-8 -*-
# coding:utf-8
import json
import wejudge.kernel.general as kernel
import wejudge.apps.problem.models as ProblemMdl
import wejudge.apps.asgn.models as AsgnModel
import wejudge.apps.contest.models as ContestModel
import time

__author__ = 'lancelrq'


class JudgeStatus(kernel.ViewerFramework):
    """评测状态展示列表"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'judge_status'

    def status_list(self, page=1, limit=50):
        """
        评测状态列表
        :param page: 分页信息
        :param limit: 每页显示数量
        :param status_set: 查询集合
        :return:
        """
        jst, dst = self._get_status_list(ProblemMdl.JudgeStatus.objects)
        count = jst.count()
        if count > 0:
            pager = kernel.PagerProvider(count, limit, page, 'problem_judge_status',_get=self._request.GET)
            jdugestatus = jst.all()[pager.start_idx: pager.start_idx + limit]
            pager = pager.render()
        else:
            pager = ""
            jdugestatus = None

        self._template_file = 'problem/status/list.html'
        self._context = {
            'pager': pager,
            'status_list': jdugestatus,
        }
        self._context.update(dst)

    def status_list_in_problem(self, pid):
        """
        在某题我的评测记录
        :return:
        """
        if not self._check_login(True, True):
            return
        if pid is not None:
            jst = ProblemMdl.JudgeStatus.objects.filter(problem_id=pid, author_id=self._user_session.user_id).order_by("-id")
            count = jst.count()
            if count > 20:
                count = 20
            jdugestatus = jst.all()[:count]
        else:
            jdugestatus = None
        self._template_file = 'problem/status/list_body.html'
        self._context = {
            'status_list': jdugestatus
        }

    def judge_detail(self, sid):
        """
        评测机报告页面
        :param sid: 评测状态记录
        :return:
        """

        # asgn_id = self._request.GET.get('asgn_id', None)
        # contest_id = self._request.GET.get('contest_id', None)
        if not self._user_session.is_logined():
            self._action = kernel.const.VIEW_ACTION_LOGIN_REQUEST
            self._redirect_url = self._request.path
            return

        status = self._get_judge_status_detail(sid)
        # 如果当前评测状态不存在
        if status is None:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_READ_JUDGE_RESULT_FAILED
            return

        try:
            if status.callback is not None and status.callback.strip() != '':
                callback = json.loads(status.callback)
            else:
                callback = None
        except:
            callback = None

        asgn_id = None
        contest_id = None

        if callback is not None:
            if callback.get('provider', '') == 'asgn':
                asgn_id = callback.get('id')
            elif callback.get('provider', '') == 'contest':
                contest_id = callback.get('id')

        if contest_id is not None:
            contest = ContestModel.Contest.objects.filter(id=contest_id)
            if contest.exists():
                contest = contest[0]
                if self._user_session.user_id != contest.author.id and contest.end_time < int(time.time()):
                    self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                    self._context = kernel.error_const.ERROR_CONTEST_VISIT_STATUS_AFTER_CONTEST_ENDED
                    return

        # 如果这个评测状态不是由当前用户生成的
        if self._user_session.user_id != status.author.id:
            # 如果这是一个比赛的评测状态
            if contest_id is not None:
                contest = ContestModel.Contest.objects.filter(id=contest_id)
                if contest.exists():
                    contest = contest[0]
                    referees = str(contest.referees).split('\n')
                    referees.append(str(contest.author.id))
                    if str(self._user_session.user_id) not in referees:
                        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                        self._context = kernel.error_const.ERROR_JUDGE_RESULT_ONLY_USER
                        return
                else:
                    self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                    self._context = kernel.error_const.ERROR_JUDGE_RESULT_ONLY_USER
                    return
            else:
                # 如果当前用户不是老师、管理员中任意角色
                if self._user_session.user_role not in [2, 3, 99]:
                    if asgn_id is not None:
                        asgn = AsgnModel.Asgn.objects.filter(id=asgn_id)
                        if asgn.exists():
                            # 助教检查
                            if not asgn[0].course.assistants.filter(id=self._user_session.user_id).exists():
                                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                                self._context = kernel.error_const.ERROR_JUDGE_RESULT_ONLY_USER
                                return
                        else:
                            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                            self._context = kernel.error_const.ERROR_JUDGE_RESULT_ONLY_USER
                            return
                    else:
                        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                        self._context = kernel.error_const.ERROR_JUDGE_RESULT_ONLY_USER
                        return
                # 如果当前用户是老师，但是题目设置了私有查看
                if (self._user_session.user_role != 99) and (status.problem.is_private is True):
                    self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                    self._context = kernel.error_const.ERROR_JUDGE_RESULT_ONLY_USER
                    return
        try:
            if status.result is not None and status.result != '':
                result = json.loads(status.result)
            else:
                result = {}

            upstor = kernel.LocalStorage(kernel.const.USER_UPLOADCODE_DIR, '')
            upload_code = upstor.read_file(status.code_path)

            testdata_detail = None

            if status.flag in [0, 1, 2, 3, 4, 5, 6]:            # 已有评测数据

                outdatas = result.get('outdatas', {})
                detail = result.get('result', {})
                odstor = kernel.LocalStorage(kernel.const.PROGRAM_RUN_OUTDATAS, str(status.id))
                tdstor = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(status.problem.id))
                testdatas = status.problem.test_data.order_by('order')
                testdata_detail = []
                for td in testdatas:
                    v = detail.get(td.handle, {})
                    if v.get('result', -3) not in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
                        continue
                    d = {
                        "memoryused": v.get('memoryused', 0),
                        "timeused": v.get('timeused', 0),
                        "result": v.get('result', -3),
                        "handle": td.handle,
                        "name": td.name,
                        "signal": v.get('re_signum', 0),
                        "signal_desc": kernel.const.SIGNUM_DESC.get(v.get('re_signum', 0), '未知'),
                    }
                    # 如果不是管理员或者老师，并且设置了隐藏测试数据
                    if (not td.visible) and (self._user_session.user_role not in [2, 3, 99]):
                        d['forbidden'] = True
                    else:
                        if v.get('result', -3) in [0, 1, 4, 6]:
                            infile_size = tdstor.get_file_size('%s.in' % td.handle)
                            outfile_size = tdstor.get_file_size('%s.out' % td.handle)
                            odfile_size = odstor.get_file_size('%s.outdata' % td.handle)
                            if (infile_size > 2 * 100 *1024) or (outfile_size > 2 * 100 * 1024) or (odfile_size > 2 * 100 * 1024):
                                d['too_large'] = True
                                testdata_detail.append(d)
                                continue
                            try:
                                d['in'] = tdstor.read_file('%s.in' % td.handle).encode("utf-8")
                            except:
                                d['in'] = "出现错误的字符，系统无法解码，请检查程序输出"
                            try:
                                d['out'] = tdstor.read_file('%s.out' % td.handle).encode("utf-8")
                            except:
                                d['out'] = "出现错误的字符，系统无法解码，请检查程序输出"
                            try:
                                d['outdata'] = odstor.read_file('%s.outdata' % td.handle).encode("utf-8")
                            except:
                                d['outdata'] = "出现错误的字符，系统无法解码，请检查程序输出"

                    testdata_detail.append(d)

                pass

            self._template_file = "problem/status/detail.html"
            self._context = {
                'status': status,
                'result': result,
                'detail': testdata_detail,
                'upload_code': upload_code
            }

        except BaseException, ex:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_READ_JUDGE_RESULT_FAILED
            return

    def get_filter_page(self):
        """
        获取过滤器列表
        :return:
        """
        problem_id = self._request.GET.get('problem_id', '')
        author_type = self._request.GET.get('author_type', '')
        author_id = self._request.GET.get('author_id', '')
        flag = self._request.GET.get('flag', '')
        if flag is not None and flag.strip() == '':
            flag = -3
        else:
            try:
                flag = int(flag)
            except:
                flag = -3
            finally:
                if flag < -3 or flag > 9:
                    flag = -3
        self._template_file = "problem/status/filter.html"
        kernel.const.JUDGE_STATUS_FLAG_DESC.iteritems()
        self._context = {
            "problem_id": problem_id,
            "author_id": author_id,
            "author_type": author_type,
            "flag": flag,
            "flags": kernel.const.JUDGE_STATUS_FLAG_DESC.iteritems()
        }

    def _get_status_list(self, status_set, desc=True):
        """
        评测状态列表查询
        :param problem_id:
        :param author_id:
        :param flag:
        :param desc:
        :return:
        """
        problem_id = self._request.GET.get('problem_id', '')
        if problem_id is not None and problem_id.strip() == '':
            problem_id = None
        author_id = self._request.GET.get('author_id', '')
        if author_id is not None and author_id.strip() == '':
            author_id = ""
        flag = self._request.GET.get('flag', '')
        if flag is not None and flag.strip() == '':
            flag = -3
        else:
            try:
                flag = int(flag)
            except:
                flag = -3
            finally:
                if flag < -3 or flag > 9:
                    flag = -3
        author_type = self._request.GET.get('author_type', '')
        author = "%s%s" % (author_type, author_id)

        jst = status_set

        if flag > -3:
            jst = jst.filter(flag=flag)

        if problem_id is not None:
            try:
                pid = int(problem_id)
                jst = jst.filter(problem__id=pid)
            except:
                pass

        if (author is not None) and (author.strip() != ""):

            if author[:3] == '[n]':
                jst = jst.filter(author__nickname__contains=author[3:])
            elif author[:3] == '[r]':
                jst = jst.filter(author__realname__contains=author[3:])
            else:
                jst = jst.filter(author__id__contains=author)

        if desc:
            jst = jst.order_by('-id')

        return jst, {
            'flag': flag,
            'author_id': author_id,
            'author_type': author_type,
            'problem_id': problem_id
        }

    def _get_judge_status_detail(self, status_id):
        js = ProblemMdl.JudgeStatus.objects.filter(id=status_id)
        if js.exists():
            return js[0]
        else:
            return None
