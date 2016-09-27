# -*- coding: utf-8 -*-
# coding:utf-8

import os
import time
import uuid
import xlrd
import xlwt
import zipfile
import wejudge.apps.problem.models as ProblemMdl
import wejudge.kernel.education as EduKernel
import wejudge.apps.asgn.models as AsgnModel
import wejudge.apps.education.models as EduModel
import wejudge.kernel.general as kernel
import AsgnProvider as Provider

__author__ = 'lancelrq'


class AsgnAnalyzer(Provider.AsgnProvider, EduKernel.EduCenterProvider):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'asgn'

    def __check_permission_only(self, asgn=None):
        """
        检查权限
        :param asgn: 作业
        :return:
        """
        if self._user_session.user_role == 99:
            return True
        elif self._user_session.user_role == 2:
            if asgn is None:        # 表示不用检查作业拥有权身份
                return True
            # 判断题目为当前用户拥有
            if self._user_session.user_id == asgn.author.id:
                return True
            else:
                return False
        else:
            return False

    def asgn_public_statistics_analyzer(self, asgn_id):
        """
        作业统计模块
        :param asgn_id:

        :return:
        """

        self._action = kernel.const.VIEW_ACTION_JSON
        """
        if not self._check_login(True):
            return
        """
        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '未找到作业信息')
            return
        """
        if not self.__check_permission_only(asgn):
            self._action = kernel.const.VIEW_ACTION_JSON
            self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            return
        """
        result = self._asgn_analyzer(asgn)
        self._result = kernel.RESTStruct(True, data=result)

    def asgn_score_counter(self, course_id):
        """
        作业成绩统计提供程序
        :param course_id:
        :return:
        """
        if self._user_session.user_role not in [2, 99]:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_ADMIN_PERMISSION_DENIED
            return
        course = self._get_course_by_id(course_id)
        if course is None:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_EDU_COURSE_NOT_FOUND
            return
        asgn_ids = self._request.POST.getlist('aids')

        type = self._request.POST.get('type', 'all')
        if type == 'stucode':
            files = self._request.FILES.get('stuno_xls')
            if files is not None:
                stucodes = []
                path = "asgn_score_counter/%s.xls" % (uuid.uuid4())
                file_name = os.path.join(kernel.const.IMPORT_PROCESS_TEMP_DIR, path)
                destination = open(file_name, 'wb+')
                for chunk in files.chunks():
                    destination.write(chunk)
                destination.close()
                xls_sheet = xlrd.open_workbook(file_name)
                xls_table = xls_sheet.sheet_by_index(0)
                for i in range(1, xls_table.nrows):
                    stucodes.append(str(xls_table.row_values(i)[0]))
                print stucodes
            else:
                stucodes = None
        else:
            stucodes = None

        stu_score = self._asgn_score_count(course, asgn_ids, stucodes)
        fn, fp = self._export_score_to_xls(course, asgn_ids, stu_score, stucodes)

        self._action = kernel.const.VIEW_ACTION_DOWNLOAD
        self._context = kernel.LocalStorage(kernel.const.EXPORT_PROCESS_TEMP_DIR, 'asgn_score_counter')
        self._template_file = fn
        self._download_filename = "score.xls"
        return

    def _asgn_score_count(self, course, asgn_ids, stucodes):
        """
        成绩统计实现
        :param course:
        :return:
        """
        asgn_switch = asgn_ids
        asgn_ratios = {}
        asgn_total = 100.0
        asgn_total_cnt = len(asgn_switch)
        for asgn_id in asgn_switch:
            ratio = self._request.POST.get('ratio_%s' % asgn_id, '')
            try:
                ratio = float(ratio)
            except:
                ratio = 0
            if ratio < 0 or ratio >100:
                ratio = 0
            if ratio != 0:
                asgn_ratios[asgn_id] = ratio        # 写入自定义的比例比例
                asgn_total -= ratio
                asgn_total_cnt -= 1
        if asgn_total_cnt > 0:
            for asgn_id in asgn_switch:
                if not asgn_ratios.has_key(asgn_id):
                    asgn_ratios[asgn_id] = asgn_total / asgn_total_cnt

        stu_score = {}

        for asgn_id in asgn_switch:
            asgn = course.asgn_set.filter(id=asgn_id)
            if not asgn.exists():
                continue
            asgn = asgn[0]
            ratio = asgn_ratios.get(asgn_id, 0)
            stu_reports = AsgnModel.StuReport.objects.filter(asgn=asgn).all()

            for report in stu_reports:

                if stucodes is not None:
                    if str(report.student.id) not in stucodes:
                        continue

                sc = stu_score.get(report.student.id, {"student_name": report.student.realname})
                avg = sc.get('avg', 0)
                avg += report.finally_score * (ratio / 100.0)
                sc[asgn_id] = report.finally_score
                sc['avg'] = avg
                stu_score[report.student.id] = sc

        return stu_score


    def _export_score_to_xls(self, course, asgn_ids, stu_score, stucodes):
        """
        导出成绩统计到excel
        :return:
        """
        asgn_list = course.asgn_set.all()
        asgn_namelist = {}
        for asgn in asgn_list:
            asgn_namelist[unicode(asgn.id)] = asgn.name

        filename = "%s.xls" % uuid.uuid4()
        filepath = "%s/%s/%s" % (kernel.const.EXPORT_PROCESS_TEMP_DIR, 'asgn_score_counter', filename)
        xlsfile = xlwt.Workbook()
        table = xlsfile.add_sheet(u'成绩统计')
        i = 1
        j = 2
        table.write(0, 0, u"学号")
        table.write(0, 1, u"姓名")
        for asgn_id in asgn_ids:
            table.write(0, j, asgn_namelist[asgn_id])
            j += 1
        table.write(0, j, u"加权平均分")

        if stucodes is None:
            for key, score in stu_score.iteritems():
                table.write(i, 0, key)
                table.write(i, 1, unicode(score.get('student_name', '')))
                j = 2
                for asgn_id in asgn_ids:
                    table.write(i, j, score.get(asgn_id, 0))
                    j += 1
                table.write(i, j, score.get('avg', 0))
                i += 1
        else:
            for code in stucodes:
                score = stu_score.get(code, {})
                table.write(i, 0, code)
                table.write(i, 1, unicode(score.get('student_name', '')))
                j = 2
                for asgn_id in asgn_ids:
                    table.write(i, j, score.get(asgn_id, 0))
                    j += 1
                table.write(i, j, score.get('avg', 0))
                i += 1

        xlsfile.save(filepath)
        return filename, filepath

    @staticmethod
    def _asgn_analyzer(asgn, days=7):
        """
        统计模块调用
        :param asgn:
        :param days: 天数
        :return:
        """
        # 常量
        TIME_INTERVAL = 600  # 间隔时间，60秒
        FIRST_SUB_TIME = -1  # 第一次提交的时间
        ERROR_CODES = {
            1: 0,                   # PE类
            2: 2,                   # TLE类
            3: 3,                   # MLE类
            4: 1,                   # 内容错误类
            5: 4,                   # RE类
            6: 1,                   # 内容错误类
            7: 5                    # CE类
        }
        # 学生列表
        asgn_students = []
        # 时间线表
        asgn_timeline_row = {}
        asgn_timeline = {}
        # 问题统计表
        problem_counter = {}
        # 错误计数表
        asgn_errors = [0, 0, 0, 0, 0, 0]
        # 首先取得当前作业对于的排课信息
        arrangements = asgn.course.arrangements.all()
        for arr in arrangements:
            students = arr.students.all()
            for stu in students:
                asgn_students.append(stu.id)            # 取得作业的学生数据
        statuses = asgn.judge_status.all()              # 取得评测历史记录表(不使用order_by了）
        for status in statuses:
            if status.author.id not in asgn_students:   # 排除项目
                continue
            if FIRST_SUB_TIME == -1:                    # 设置第一次提交的时间
                FIRST_SUB_TIME = status.timestamp
                for i in range(0, int(days * 86400 / TIME_INTERVAL)):
                    asgn_timeline_row[i] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                pass
            # 获取某个问题的计数器
            pc_item = problem_counter.get(status.problem.id, [0, 0, 0, 0, 0, 0, 0, 0, 0, status.problem.title])
            if (status.flag >= 0) and (status.flag <= 8):
                pc_item[status.flag] += 1
            problem_counter[status.problem.id] = pc_item
            # 当前记录时间减去第一次的时间，再用间隔数来除这个时间作为hash
            tl_key = int((status.timestamp - FIRST_SUB_TIME) / TIME_INTERVAL)
            tl_item = asgn_timeline_row.get(tl_key, None)     # 取得统计过的记录
            if tl_item is None:
                continue
            tl_item[0] += 1                                 # 总提交计数
            if (status.flag >= 0) and (status.flag <= 8):   # 如果属于正常评测结果
                tl_item[status.flag + 1] += 1
                asgn_timeline_row[tl_key] = tl_item         # 写回
            if status.flag in ERROR_CODES.keys():
                er_key = ERROR_CODES.get(status.flag, 4)
                asgn_errors[er_key] += 1     # 写回

        for key, value in asgn_timeline_row.iteritems():
            for i in range(0, 9):        # len(value)
                item = asgn_timeline.get(i, [])
                item.append(value[i])
                asgn_timeline[i] = item

        return {
            'time_zoom': TIME_INTERVAL * 1000,
            'time_interval': TIME_INTERVAL * 1000,
            'start_time': FIRST_SUB_TIME,
            'timeline': asgn_timeline,
            'errors': asgn_errors,
            'problem_counter': problem_counter
        }