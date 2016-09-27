# -*- coding: utf-8 -*-
# coding:utf-8

import json
import time
import datetime
import wejudge.apps.problem.models as ProblemMdl
import wejudge.kernel.education as EduKernel
import wejudge.apps.asgn.models as AsgnModel
import wejudge.apps.education.models as EduModel
import wejudge.kernel.general as kernel
import AsgnProvider as Provider
import uuid
import zipfile

__author__ = 'lancelrq'


class AsgnManager(Provider.AsgnProvider, EduKernel.EduCenterProvider):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'asgn'

    def _get_view_term(self):
        """
        @override 由于不需要查看别的学期的课程，所以覆盖父类同名方法
        :return:
        """
        return {'year': self._config.year, 'term': self._config.term}

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

    def __check_permission(self, asgn=None, ajax=False, no_redirect=False):
        """
        检查权限（包含渲染数据处理，也就是说调用完的结果为False时只要return即可，不必再写渲染代码）
        :param problem: 作业
        :ajax problem: 是否为ajax请求
        :param owner_only: 仅允许拥有者操作（管理员无效）
        :param no_redirect: 禁用错误页面跳转
        :return:
        """
        flag = self.__check_permission_only(asgn)
        if flag is False:
            if no_redirect:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "[ERROR]当前账户没有操作权限"
                return flag
            if ajax:
                self._action = kernel.const.VIEW_ACTION_JSON
                self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            else:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ADMIN_PERMISSION_DENIED
        return flag

    def asgn_problem_setting_ajax(self, asgn_id, asgn_problem_id):
        """
        展示当前作业中某道题目的设置
        """
        if not self._check_login(True, True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True, True):
            return

        ap = asgn.problemset.filter(id=asgn_problem_id)
        if ap.exists():
            self._template_file = "asgn/manager/ajax_problem_setting.html"
            self._context = {
                "asgn_problem": ap[0],
                "asgn": asgn
            }
        else:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "Unknow Asgn_Problem ID."

    def remove_asgn_problem(self, asgn_id, asgn_problem_id):
        """
        移除当前作业中的某道题目，但不删除题目本体
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True):
            return

        ap = asgn.problemset.filter(id=asgn_problem_id)
        if ap.exists():
            asgn.problemset.remove(ap[0])
            self._result = kernel.RESTStruct(True)
        else:
            self._result = kernel.RESTStruct(False, "题目信息未知")

    def save_asgn_problem_setting(self, asgn_id, asgn_problem_id):
        """
        保存当前作业中某道题目的设置
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True):
            return

        ap = asgn.problemset.filter(id=asgn_problem_id)
        if not ap.exists():
            self._result = kernel.RESTStruct(False, "找不到该题目设置")
            return
        ap = ap[0]

        score = self._request.POST.get("score", "")
        if not str.isdigit(str(score)):
            self._result = kernel.RESTStruct(False, "分数值非法，请不要输入负数或者非数字符")
            return
        score = int(score)

        lang = self._request.POST.getlist("lang")
        if len(lang) == 0:
            self._result = kernel.RESTStruct(False, "请至少分配一种评测语言")
            return
        cnt = 0
        asgn_lang = asgn.lang.split(",") if asgn.lang != 'all' else kernel.const.LANGUAGE_PROVIDE
        for i in lang:
            if i not in asgn_lang:
                cnt += 1
        if cnt == 0 and (len(lang) == len(asgn_lang)):
            lang = 'inherit'
        else:
            lang = ','.join(lang)

        require = True if self._request.POST.get('require', '0') == '1' else False

        ap.score = score
        ap.lang = lang
        ap.require = require
        ap.save()

        self._result = kernel.RESTStruct(True)

    def _set_asgn_setting(self, course, asgn=None):
        """
        作业设置内部处理程序
        :param course: 归属课程
        :param asgn: 作业类，None则新建
        :return:
        """
        name = self._request.POST.get("name", "")
        if name.strip() == '':
            self._result = kernel.RESTStruct(False, "请输入作业名称")
            return False

        score = self._request.POST.get("full_score", "")
        if not str.isdigit(str(score)):
            self._result = kernel.RESTStruct(False, "分数值非法，请不要输入负数或者非数字符")
            return False
        score = int(score)

        remark = self._request.POST.get("remark", "")

        lang = self._request.POST.getlist("lang", "")
        if len(lang) == 0:
            self._result = kernel.RESTStruct(False, "请至少分配一种评测语言")
            return False
        cnt = 0
        asgn_lang = kernel.const.LANGUAGE_PROVIDE
        for i in lang:
            if i in asgn_lang:
                cnt += 1
        if cnt == len(asgn_lang):
            lang = 'all'
        else:
            lang = ','.join(lang)

        if asgn is None:
            asgn = AsgnModel.Asgn()
            asgn.author = self._user_session.entity
            asgn.create_time = int(time.time())

        asgn.course = course
        asgn.remark = remark
        asgn.lang = lang
        asgn.name = name
        asgn.full_score = score
        asgn.save()

        return True

    def new_asgn(self, course_id):
        """新建作业"""
        if not self._check_login(True, True):
            return

        if self._user_session.user_role != 2:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "非教师账户不能发布作业"
            return

        course = self._get_course_by_id(course_id)
        if course is None:
            return

        course_list = self._get_course_choosing(self._get_view_term())
        self._template_file = "asgn/manager/setting_body.html"
        self._context = {
            "setting_type": "new",
            "course": course,
        }

    def save_new_asgn(self, course_id):
        """
        保存当前作业的设置
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        course = self._get_course_by_id(course_id)
        if course is None:
            self._result = kernel.RESTStruct(False, "课程不存在")
            return

        if self._set_asgn_setting(course):
            self._result = kernel.RESTStruct(True)

    def asgn_setting(self, asgn_id):
        """
        作业设置
        """
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self.__check_permission(asgn):
            return

        course_list = self._get_course_choosing(self._get_view_term())
        self._template_file = "asgn/manager/setting.html"
        self._context = {
            "type": "setting",
            "courseList": course_list,
            "asgn": asgn,
            'problem_list': self._get_problem_list(asgn)
        }

    def save_asgn_setting(self, asgn_id):
        """
        保存当前作业的设置
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True):
            return

        course = self._request.POST.get("course", "")
        course = self._get_course_by_id(course)
        if course is None:
            self._result = kernel.RESTStruct(False, "请选择课程或是选择的课程不存在")
            return

        if self._set_asgn_setting(course, asgn):
            self._result = kernel.RESTStruct(True)

    def add_problems(self, asgn_id):
        # 增加题目接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._result = kernel.RESTStruct(False, msg="作业不存在")
            return

        if not self.__check_permission(asgn, True):
            return

        problem_ids = self._request.POST.getlist('problem_ids')
        if len(problem_ids) == 0:
            self._result = kernel.RESTStruct(False, msg="请选择要操作的项目")
            return

        ps = ProblemMdl.Problem.objects.filter(id__in=problem_ids)

        failed = []

        for p in ps:
            if not asgn.problemset.filter(problem=p).exists():
                ap = AsgnModel.AsgnProblems()
                ap.problem = p
                ap.require = True
                ap.save()
                asgn.problemset.add(ap)
            else:
                failed.append("%s. %s<br />" % (p.id, p.title))

        if len(failed) > 0:
            self._result = kernel.RESTStruct(True, msg=u"添加成功！<br />但是我们发现您选择了一些重复的题目，因此以下题目将不会被重复添加：<br /><strong>" + u"".join(failed) +  "</strong>点击确定后自动返回作业的题目列表，请刷新页面，并对新添加的题目进行设置。")
        else:
            self._result = kernel.RESTStruct(True, msg=u"添加成功！<br />点击确定后自动返回作业的题目列表，请刷新页面，并对新添加的题目进行设置。")

        self._request.session["problem_archive_choosing_to_asgn"] = 0

    def asgn_checkup_list(self, asgn_id):
        """作业批改"""
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self._is_course_assistants(asgn.course):         # 如果不是助教
            if not self.__check_permission(asgn):               # 没有管理权限
                return


        report_list_temp = {}
        report_list = []
        reports = AsgnModel.StuReport.objects.filter(asgn=asgn)
        for rep in reports:
            report_list_temp[rep.student.id] = rep
        for arr in asgn.access_control.all():
            for stu in arr.arrangement.students.all():
                if not report_list_temp.has_key(stu.id):
                    report_list_temp[stu.id] = {
                        "student": {
                            "id": stu.id,
                            "realname": stu.realname
                        },
                        "created": False
                    }
        for key, rpitem in report_list_temp.iteritems():
            report_list.append(rpitem)

        course_list = self._get_course_choosing(self._get_view_term())
        self._template_file = "asgn/manager/checkup_list.html"
        self._context = {
            "type": "checkup",
            "asgn": asgn,
            "report_list": report_list,
            'problem_list': self._get_problem_list(asgn)
        }

    def save_asgn_checkup(self, asgn_id, report_id):
        """保存作业批改"""

        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self._is_course_assistants(asgn.course):             # 如果不是助教
            if not self.__check_permission(asgn, True):             # 没有管理权限
                return

        report = AsgnModel.StuReport.objects.filter(asgn=asgn, id=report_id)
        if not report.exists():
            self._result = kernel.RESTStruct(False, "实验报告不存在")
            return

        report = report[0]

        remark = self._request.POST.get("remark", "")
        score = self._request.POST.get("score", report.judge_score)
        if not str.isdigit(str(score)):
            self._result = kernel.RESTStruct(False, "分数值非法，请不要输入负数或者非数字符")
            return False
        score = int(score)
        if score > asgn.full_score:
            score = asgn.full_score

        report.teacher_check = True
        report.finally_score = score
        report.teacher_remark = remark
        report.save()

        self._result = kernel.RESTStruct(True)

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
        report.save()

    def save_asgn_checkup_fast(self, asgn_id):
        """一键批改作业"""

        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self._is_course_assistants(asgn.course):             # 如果不是助教
            if not self.__check_permission(asgn, True):             # 没有管理权限
                return

        remark = self._request.POST.get("teacher_remark", "")
        score = self._request.POST.get("teacher_score", "")
        use_judge_score = self._request.POST.get("use_judge_score", "")
        use_judge_score = True if (use_judge_score == '1') else False
        refresh_judge_score = self._request.POST.get("refresh_judge_score", "")
        refresh_judge_score = True if (refresh_judge_score == '1') else False

        try:
            score = int(score)
        except Exception, ex:
            score = asgn.full_score

        sids = self._request.POST.getlist("sids")

        reports = AsgnModel.StuReport.objects.filter(asgn=asgn, student__id__in=sids)
        for report in reports:
            if refresh_judge_score:
                self.__asgn_report_count_by_solutions(asgn, report)
            report.teacher_check = True
            report.finally_score = report.judge_score if use_judge_score else score
            report.teacher_remark = remark
            report.save()


        self._result = kernel.RESTStruct(True)

    def asgn_arrangement(self, asgn_id):
        """作业排课设置"""
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self.__check_permission(asgn):
            return

        arrangement_list = asgn.course.arrangements.all()
        for arrangement in arrangement_list:
            if not asgn.access_control.filter(arrangement=arrangement).exists():
                ac = AsgnModel.AsgnAccessControl()
                ac.arrangement = arrangement
                ac.start_time = 0
                ac.end_time = 0
                ac.enabled = False
                ac.save()
                asgn.access_control.add(ac)

        access_list = asgn.access_control.all()

        self._template_file = "asgn/manager/arrangement.html"
        self._context = {
            "type": "arrangement",
            "asgn": asgn,
            "arrangement_list": arrangement_list,
            "access_list": access_list,
            'problem_list': self._get_problem_list(asgn)
        }

    def save_asgn_arrangement(self, asgn_id):
        """保存排课设置"""

        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True):
            return

        aids = self._request.POST.getlist("aids")
        access_list = asgn.access_control.all()
        for access in access_list:
            if str(access.id) not in aids:
                access.enabled = False
            else:
                access.enabled = True
            access.save()

        for id in aids:
            access = asgn.access_control.filter(id=id)
            if access.exists():
                access = access[0]
            try:
                access.start_time = time.mktime(datetime.datetime.strptime(self._request.POST.get("start_time_" + id), "%Y-%m-%d %H:%M:%S").timetuple())
                access.end_time = time.mktime(datetime.datetime.strptime(self._request.POST.get("end_time_" + id), "%Y-%m-%d %H:%M:%S").timetuple())
            except:
                access.start_time = 0
                access.end_time = 0
            finally:
                access.save()

        self._result = kernel.RESTStruct(True)

    def asgn_mgr_visit_require(self, asgn_id):
        """作业调课管理"""
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self.__check_permission(asgn):
            return

        require_list = AsgnModel.AsgnVisitRequirement.objects.filter(asgn=asgn).order_by("-flag")

        self._template_file = "asgn/manager/visit_require.html"
        self._context = {
            "type": "visit_reqire",
            "asgn": asgn,
            "require_list": require_list,
            'problem_list': self._get_problem_list(asgn)
        }

    def save_mgr_visit_require(self, asgn_id):
        """保存调课管理操作"""

        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return   # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True):
            return

        action = self._request.POST.get("action", -1)
        rids = self._request.POST.getlist("rids")
        if len(rids) == 0:
            self._result = kernel.RESTStruct(False, "请选择项目")
            return
        try:
            action = int(action)
            if action not in [-2, 0, 1]:
                self._result = kernel.RESTStruct(False, "参数错误")
                return
        except:
            self._result = kernel.RESTStruct(False, "参数错误")
            return

        for rid in rids:
            req = AsgnModel.AsgnVisitRequirement.objects.filter(id=rid)
            if req.exists():
                req = req[0]
                if action == -2:
                    req.delete()
                    continue
                if action == 0:
                    req.flag = 0
                elif action == 1:
                    req.flag = 1
                req.proc_time = int(time.time())
                req.save()

        self._result = kernel.RESTStruct(True)

    def asgn_statistics(self, asgn_id):
        """
        统计模块
        :param asgn_id:
        :return:
        """

        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self.__check_permission(asgn):
            return

        self._template_file = "asgn/manager/statistics.html"
        self._context = {
            "type": "statistics",
            "asgn": asgn,
            'problem_list': self._get_problem_list(asgn)
        }

    def asgn_zip_code_config(self, asgn_id):
        """
        代码打包配置
        :param asgn_id:
        :return:
        """
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self.__check_permission(asgn):
            return

        self._template_file = "asgn/manager/zip_code.html"
        self._context = {
            "type": "zip_code",
            "asgn": asgn,
            'problem_list': self._get_problem_list(asgn)
        }

    def asgn_delete_view(self, asgn_id):
        """
        删除作业
        :param asgn_id:
        :return:
        """
        if not self._check_login():
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._send_err_asgn_do_not_exist()
            return

        if not self.__check_permission(asgn):
            return

        self._template_file = "asgn/manager/delete.html"
        self._context = {
            "type": "delete",
            "asgn": asgn,
            'problem_list': self._get_problem_list(asgn)
        }

    def asgn_delete(self, asgn_id):
        # 删除作业接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            return  # 不返回结果，没什么好说的，非法调用接口了都

        if not self.__check_permission(asgn, True):
            return

        confrim = self._request.POST.get('confrim', '0')
        if str(confrim) != '1':
            self._result = kernel.RESTStruct(False, '请先阅读并且同意此操作需要承担的风险')
            return

        asgn.delete()
        self._result = kernel.RESTStruct(True)

    def asgn_zip_the_codes(self, asgn_id):
        """
        打包代码实现程序
        :param asgn
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        asgn = self._get_asgn_detail(asgn_id)
        if asgn is None:
            self._result = kernel.RESTStruct(False, u'未找到作业')
            return
        if not self.__check_permission(asgn, True):
            return
        encoding = self._request.POST.get('encoding', 'gbk')
        separators = self._request.POST.get('separators', '\\')
        if separators != '\\' and separators != '/':
            separators = '\\'
        filename = "%s.zip" % uuid.uuid4()
        filepath = "%s/%s/%s" % (kernel.const.EXPORT_PROCESS_TEMP_DIR, 'asgn_zip', filename)
        storage = kernel.LocalStorage(kernel.const.USER_UPLOADCODE_DIR, '')
        zf = zipfile.ZipFile(filepath, "w", zipfile.zlib.DEFLATED)
        judge_status = asgn.judge_status.filter(flag=0)
        for status in judge_status:
            if not storage.exists(status.code_path):
                return
            upload_code = storage.get_file_path(status.code_path)
            stor_name = u"%s_%s%c%s_%s.%s" % (
                status.author.id, status.author.realname,
                separators, status.problem.id, status.id,
                kernel.const.SOURCE_CODE_EXTENSION.get(status.lang)
            )
            if encoding == 'utf-8':
                zf.write(upload_code, stor_name)
            else:
                zf.write(upload_code, stor_name.decode('utf-8').encode('gbk'))
        zf.close()
        self._result = kernel.RESTStruct(True, data=filename)
        return
