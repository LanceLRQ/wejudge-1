# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import json
import time
import wejudge.kernel.general as kernel
import wejudge.apps.asgn.models as AsgnModel

class AsgnProvider(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'asgn'

    def _get_asgn_arrangement(self, asgn):
        """
        作业选课检查（学生账户）
        :param asgn:
        :return:
        """
        vreq = AsgnModel.AsgnVisitRequirement.objects.filter(author=self._user_session.entity, asgn=asgn, flag=1)
        if vreq.exists():
            vreq = vreq[0]
            varg = asgn.access_control.filter(enabled=True, arrangement=vreq.arrangement)
            if varg.exists():
                varg = varg[0]
                return True, varg.start_time, varg.end_time
        access_list = asgn.access_control.filter(enabled=True)
        start_time = 4294967295
        end_time = -1
        if not access_list.exists():
            return False, 0, 0
        for access in access_list:
            stus = access.arrangement.students.filter(id=self._user_session.user.id)
            if stus.exists():
                start_time = min(start_time, access.start_time)
                end_time = max(end_time, access.end_time)
        if start_time == 4294967295 and end_time == -1:
            return False, 0, 0

        return True, start_time, end_time         # 返回第一条选课记录（理论上是，排课系统会剔除重复选课记录）

    def _is_course_assistants(self, course):
        """
        检测当前用户是否为当前课程的助教
        :param course:
        :return:
        """
        if course.assistants.filter(id=self._user_session.user_id).exists():
            return True
        else:
            return False

    def _get_asgn_detail(self, asgn_id):
        """
        通过作业ID获取作业信息
        :param asgn_id:
        :return:
        """
        asgn = AsgnModel.Asgn.objects.filter(id=asgn_id)
        if asgn.exists():
            return asgn[0]
        else:
            return None

    def _check_asgn_permission(self, asgn):
        """
        作业访问访问权限检查（提供程序）
        :param asgn:
        :return:
        """
        if self._user_session.user_role not in [2, 99]:

            # 助教检查
            if self._is_course_assistants(asgn.course):
                check_count = AsgnModel.StuReport.objects.filter(asgn=asgn.id, teacher_check=False).count()
                return 3, check_count
            # 黑名单检查
            if asgn.black_list.filter(id=self._user_session.user_id).exists():
                return -2, -1       # 无权限
            # 排课检查
            flag, st, et = self._get_asgn_arrangement(asgn)
            if flag is False:
                return -2, -1        # 无权限
            # 时间检查
            flag, dec = kernel.GeneralTools.check_time_passed(st, et)
            return flag, dec

        else:
            # 该作业非当前教师发布
            if self._user_session.user_role == 2 and self._user_session.user_id != asgn.author.id:
                return -2, -1           # 无权限
            else:
                # 未批改数量统计
                check_count = AsgnModel.StuReport.objects.filter(asgn=asgn.id, teacher_check=False).count()
                return 2, check_count        # 管理访问

    def _check_asgn_permission_view(self, asgn):
        """作业访问访问权限检查（含渲染设置）"""
        flag, dec = self._check_asgn_permission(asgn)
        if flag not in [0, 1, 2, 3]:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_ASGN_PERMISSION_DENIED
            return False, flag, dec
        return True, flag, dec

    def _get_problem_list(self, asgn):
        """获取问题列表（不包括设置）"""
        asgn_problems = asgn.problemset.all()
        problem_list = []
        for asgn_problem in asgn_problems:
            problem_list.append(asgn_problem.problem)
        return problem_list

    def _get_langauage_limit(self, parent='all', children='inherit'):
        """
        获取语言提供列表
        :param parent: 父节点允许的语言
        :param children: 子节点允许的语言
        :return:
        """
        if parent == 'inherit' or parent == 'all':
            parent = kernel.const.LANGUAGE_PROVIDE
        else:
            parent = parent.split(",")

        if children == 'inherit':
            children = parent
        else:
            children = children.split(",")

        return children

    def _send_err_asgn_do_not_exist(self):
        """
        错误页面渲染方法：未找到作业
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_ASGN_NOT_FOUND

    def _is_my_asgn_finished(self, asgn):
        """
        返回作业完成情况
        :param asgn:
        :return:
        """
        report = AsgnModel.StuReport.objects.filter(student=self._user_session.entity, asgn=asgn)
        if report.exists():
            return True
        return False

    @staticmethod
    def _asgn_rank_list_counter(asgn, refresh=False):
        """
        排行榜计算程序
        :param asgn:
        :param refresh: 是否强制刷新
        :return:
        """
        # 初始化时间信息
        now_time = int(time.time())

        # 30秒刷新一次
        if (asgn.rank_list != '') and (not refresh) and (now_time - asgn.rank_list_cache_time < 30):
            return asgn.rank_list

        # 用户进入时间表
        user_start_time = {}
        # 读取用户的Report表
        reports = AsgnModel.StuReport.objects.filter(asgn=asgn)
        for rep in reports:
            user_start_time[rep.student.id] = rep.create_time

        # 获取用户的做题统计记录
        sols = AsgnModel.Solution.objects.values(
                "author__id", "problems__id", "author__realname", "first_ac_time", "submission", "accepted", "ignore"
        ).filter(asgn=asgn)

        rank_list = {
            'rank': [],
            'count': 0,
            'first_ac_list': {},
            'problem_list': []
        }

        # 用户临时统计数据表，排序使用
        temp_list = {}
        # 用户统计详细数据表，显示使用
        detail_list = {}
        # 第一次AC题目及其时间的数据组（临时）
        first_ac_list_tmp = {}
        # 问题列表
        problem_list = []
        aps = asgn.problemset.all()
        for ap in aps:
            problem_list.append(str(ap.problem.id))

        for sol in sols:
            # 获取用户信息
            user_id = sol.get('author__id')
            # 获取该用户的第一次进入作业的时间
            start_time = user_start_time.get(user_id, -1)
            if start_time == -1:    # 如果不存在则直接无视改用户
                continue
            problem_id = sol.get('problems__id')
            if str(problem_id) not in problem_list:      # 如果该问题不在排行榜中，则不计入
                continue
            # 获取当前用户临时统计数据表([AC计数，第一次AC时间+罚时，用户姓名]
            user_cnt = temp_list.get(user_id,  [0, 0, sol.get("author__realname")])
            # 获取当前用户统计详细数据表
            user_detail = detail_list.get(user_id, {})
            # 当前用户当前题目第一次AC的时间
            first_ac = sol.get("first_ac_time")
            # 全局：获取本题第一次AC的题目
            first_ac_item = first_ac_list_tmp.get(problem_id, 2147483647)
            # 刷新全局的第一次AC题目判定
            if (first_ac > 0) and ((first_ac - start_time) < first_ac_item):
                first_ac_item = (first_ac - start_time)
            first_ac_list_tmp[problem_id] = first_ac_item
            # 如果当前用户AC本题
            if first_ac > 0:
                # AC计数
                user_cnt[0] += 1
                # 第一次ac时间 + 错误数的罚时（SE不计入）
                user_cnt[1] = user_cnt[1] + (first_ac - start_time) + (sol.get("submission") - sol.get("accepted") - sol.get("ignore")) * 1200
                # 写入数据
                temp_list[user_id] = user_cnt
                # 写入当前题目的用户完成情况数据
            item = user_detail.get(problem_id, {})
            if first_ac > 0:
                item['first_ac'] = first_ac - start_time
            else:
                item['first_ac'] = 0
            item['sign'] = '%s_%s' % (problem_id, item['first_ac'])
            item['kda'] = 0 - (sol.get("submission") - sol.get("accepted") - sol.get("ignore"))
            # 如果用户没有过题，并且只是因为访问题目而产生了一个solution
            if item['first_ac'] == 0 and item['kda'] == 0:
                continue
            # 写入用户统计临时数据表
            user_detail[problem_id] = item
            # 写入用户统计详细数据表
            detail_list[user_id] = user_detail

        rank = []

        for k, v in temp_list.iteritems():
            rank.append((k, v[0], v[1], v[2], detail_list.get(str(k), {})))
        # 执行排序
        rank.sort(key=lambda x: (x[1], 0-x[2]), reverse=True)
        # 处理第一次AC的列表
        first_ac_list = {}
        for k, v in first_ac_list_tmp.iteritems():
            first_ac_list["%s_%s" % (k, v)] = True
        # 处理输出结果
        rank_list['rank'] = rank
        rank_list['first_ac_list'] = first_ac_list
        rank_list['problem_list'] = problem_list
        if rank is not None:
            rank_list['count'] = len(rank)
        # 序列化结果
        view_data = json.dumps(rank_list)
        asgn.rank_list = view_data
        asgn.rank_list_cache_time = now_time
        asgn.save()
        return view_data
