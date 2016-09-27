# -*- coding: utf-8 -*-
# coding:utf-8

from django.db import models
import wejudge.apps.contest.models as AppContest
import wejudge.apps.problem.models as AppProblem

__author__ = 'lancelrq'


class ContestCodeAnalysis(models.Model):

    contest = models.ForeignKey(AppContest.Contest, null=True, blank=True)                  # 对应的的比赛

    problem = models.ForeignKey(AppProblem.Problem, null=True, blank=True)                  # 对应的的题目

    status1 = models.ForeignKey(AppProblem.JudgeStatus, related_name="status1")             # 评测状态1

    status2 = models.ForeignKey(AppProblem.JudgeStatus, related_name="status2")             # 评测状态2

    levenshtein_similarity_ratio = models.FloatField(default=0)                             # Levenshtein相似度

    def __unicode__(self):
        return u"%s <-> %s: {levenshtein: %.3f%%}" % (
            self.status1.id, self.status2.id, self.levenshtein_similarity_ratio
        )

