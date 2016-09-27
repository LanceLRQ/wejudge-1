# -*- coding: utf-8 -*-
# coding:utf-8

import wejudge.apps.account.models as AccountModel
import wejudge.kernel.general as kernel
__author__ = 'lancelrq'


class RankList(kernel.ViewerFramework):
    """全站排名系统"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'ranklist'

    def RankList(self, page, limit=100):
        """显示排名情况"""
        # 排名按照问题解决数量来排序，并且按照提交通过率进行辅助排序
        userCount = AccountModel.User.objects.raw(
            """
            SELECT `id`, COUNT(`id`) AS count FROM `account_user`
            WHERE `id` NOT LIKE 'team%%%%' AND `id` != 'guest'
            LIMIT 1
            """
        )[0].count
        pager = kernel.PagerProvider(userCount, limit, page, 'account_ranklist')
        rankList = AccountModel.User.objects.raw(
            """
            SELECT `id`, `nickname`, `realname`, `motto`, `solved`, `submissions`, `accepted`,
            (`accepted` * 1.0 / `submissions`) * 100 AS `ratio`, (`submissions` - `accepted`) AS `wrong`
            FROM `account_user`
            WHERE `id` NOT LIKE 'team%%%%' AND `id` != 'guest'
            ORDER BY `solved` DESC, `wrong` ASC, `ratio` DESC
            LIMIT %s, %s
            """ % (pager.start_idx, pager.start_idx + limit)
        )
        pager_data = pager.render()
        self._template_file = 'account/ranklist.html'
        self._context = {
            'userCount': userCount,
            'start_index': pager.start_idx,
            'pager_data': pager_data,
            'rank_list': rankList,
        }