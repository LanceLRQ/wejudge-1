# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.kernel.general as kernel
import wejudge.apps.contest.models as ContestModel
import re
import time
import json
__author__ = 'lancelrq'


class ContestProvider(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'contest'

    def _check_permission(self, contest):
        """
        检查比赛服进入权限
        :param contest:
        :return:
        """

        if contest.user_limit == "all":
            return True

        if contest.author.id == self._user_session.user_id:
            return True
        referees = str(contest.referees).replace('\r', '').split('\n')

        if str(self._user_session.user_id) in referees:
            return True

        if contest.user_limit.strip() == "":
            return False

        user_limit_list = contest.user_limit.replace('\r', '').split("\n") if (contest.user_limit is not None) and (contest.user_limit.strip() != "") else []
        for item in user_limit_list:
            if str(item).strip() == '':
                continue
            if re.match(str(item), str(self._user_session.user_id)) is not None:
                return True

        return False

    def _check_admin_permission(self, contest):
        """
        检查比赛服裁判权限
        :param contest:
        :return:
        """
        referees = str(contest.referees).split('\n')
        if contest.author == self._user_session.entity:
            return True
        elif str(self._user_session.user_id) in referees:
            return True
        else:
            return False

    def _get_contest(self, contest_id):
        """
        获取比赛信息
        :param contest_id:
        :return:
        """
        if contest_id is None:
            return None
        contest = ContestModel.Contest.objects.filter(id=contest_id)
        if contest.exists():
            return contest[0]
        else:
            return None

    def _send_error_contest_doesnt_exists(self, json=False):
        """
        比赛不存在
        :return:
        """
        if json:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '比赛信息不存在')
            return
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_CONTEST_NOT_FOUND

    def _send_error_contest_permission_denied(self, json=False):
        """
        没有权限进入比赛
        :return:
        """
        if json:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '您没有权限进入比赛')
            return
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_CONTEST_PERMISSION_DENIED

    def _send_error_contest_problem_not_found(self, json=False):
        """
        没有找到比赛指定的题目
        :return:
        """
        if json:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '没有找到比赛指定的题目')
            return
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_CONTEST_PROBLEM_NOT_FOUND

    def _send_error_contest_not_start(self, json=False):
        """
        比赛还未开始
        :return:
        """
        if json:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '比赛还未开始')
            return
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_CONTEST_NOT_START

    def _send_error_contest_ended(self, json=False):
        """
        比赛已经结束
        :return:
        """
        if json:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '比赛已经结束')
            return
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_CONTEST_ENDED

    def _send_error_contest_faq_not_found(self, json=False):
        """
        未找到FAQ消息
        :return:
        """
        if json:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '未找到FAQ消息')
            return
        self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
        self._context = kernel.error_const.ERROR_CONTEST_FAQ_NOT_FOUND

    @staticmethod
    def _check_time_passed(contest):
        """
        过期检查（基于时间检查方法）
        :param contest: 比赛
        :return:
        """
        start_time = contest.start_time
        end_time = contest.end_time
        return kernel.GeneralTools.check_time_passed(start_time, end_time)

    @staticmethod
    def _rank_list_counter(contest, referee=False):
        """
        排行榜计算程序
        :param contest:
        :param referee: 是否为裁判
        :return:
        """
        # 初始化时间信息
        start_time = contest.start_time
        end_time = contest.end_time
        now_time = int(time.time())

        # 比赛结束前1小时封榜
        if (not referee) and (end_time - now_time < 3600) and contest.rank_list_1hr_stop != "":
            return contest.rank_list_1hr_stop

        # 比赛结束后1小时后开放最终榜单
        if now_time > end_time + 3600:
            return contest.rank_list

        # 30秒刷新一次
        if (contest.rank_list != '') and (not referee) and (int(time.time()) - contest.rank_list_cache_time < 30):
            return contest.rank_list


        # 读取题目问题解决数据

        rank_list = {
            'timestamp': now_time,
            'rank': [],
            'count': 0,
            'first_ac_list': {},
            'problem_list': []
        }

        # 管理员表
        admin_user_list = str(contest.referees).split('\n')
        admin_user_list.append(str(contest.author.id))

        # 用户临时统计数据表，排序使用
        temp_list = {}
        # 用户统计详细数据表，显示使用
        detail_list = {}
        # 第一次AC题目及其时间的数据组（临时）
        first_ac_list_tmp = {}
        # 问题列表
        problem_list = []
        cps = contest.problemset.all()
        for cp in cps:
            problem_list.append(str(cp.problem.id))

        sols = ContestModel.ContestSolution.objects.values(
                "problems__id", "author__id", "author__nickname", "author__realname", "author__sex",
                "first_ac_time", "submission", "accepted", "ignore"
        ).filter(contest=contest)

        for sol in sols:
            # 获取用户信息
            user_id = sol.get('author__id')
            if str(user_id) in admin_user_list:      # 管理员的提交不计入排行榜
                continue
            problem_id = sol.get('problems__id')
            if str(problem_id) not in problem_list:      # 如果该问题不在排行榜中，则不计入
                continue
            # 获取当前用户临时统计数据表([AC计数，第一次AC时间+罚时，用户昵称，用户姓名]
            nickname = '<span style="color:#f00">%s</span>' % sol.get('author__nickname', '') if sol.get('author__sex', -1) == 0 else sol.get('author__nickname', '')
            user_cnt = temp_list.get(user_id,
                 [0, 0, nickname, sol.get('author__realname', '')]
            )
            # 获取当前用户统计详细数据表
            user_detail = detail_list.get(user_id, {})
            # 当前用户当前题目第一次AC的时间
            first_ac = sol.get("first_ac_time")
            # 全局：获取本题第一次AC的题目
            first_ac_item = first_ac_list_tmp.get(problem_id, 2147483647)
            # 刷新第一次AC题目判定
            if (first_ac > 0) and ((first_ac - start_time) < first_ac_item):
                first_ac_item = (first_ac - start_time)
            first_ac_list_tmp[problem_id] = first_ac_item
            # 如果当前用户A了本题
            if first_ac > 0:
                # AC计数
                user_cnt[0] += 1
                # 总计时加上 = 第一次ac时间 + 错误数的罚时（SE不计入）
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
            # 写入用户统计临时数据表
            user_detail[problem_id] = item
            # 写入用户统计详细数据表
            detail_list[user_id] = user_detail

        rank = []

        for k, v in temp_list.iteritems():
            rank.append((k, v[0], v[1], v[2], v[3], detail_list.get(str(k), {})))
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
        if end_time - now_time >= 3600:
            contest.rank_list_1hr_stop = view_data
        contest.rank_list = view_data
        contest.rank_list_cache_time = int(time.time())
        contest.save()
        return contest.rank_list
