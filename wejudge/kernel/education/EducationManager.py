# -*- coding: utf-8 -*-
# coding:utf-8
import time
import datetime
import wejudge.apps.education.models as EduModel
import wejudge.apps.account.models as AccountModel
import wejudge.apps.asgn.models as AsgnModel
import wejudge.kernel.general as kernel
import EduCenterProvider as Provider
import os
import uuid
import xlrd
__author__ = 'lancelrq'


class EducationManager(Provider.EduCenterProvider):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'education'
        pass

    # === 鉴权 ===

    def __check_permission_only(self, course=None):
        """
        检查权限
        :param problem: 问题记录
        :param owner_only: 仅允许拥有者操作（管理员无效）
        :return:
        """
        if self._user_session.user_role == 99:
            return True
        elif self._user_session.user_role == 2:
            # 判断题目为当前用户拥有
            if self._user_session.user_id == course.teacher.id:
                return True
            else:
                return False
        else:
            return False

    def __check_permission(self, course=None, ajax=False, no_redirect=False):
        """
        检查权限（包含渲染数据处理，也就是说调用完的结果为False时只要return即可，不必再写渲染代码）
        :param course: 课程记录
        :ajax problem: 是否为ajax请求
        :param owner_only: 仅允许拥有者操作（管理员无效）
        :param no_redirect: 禁用错误页面跳转
        :return:
        """
        flag = self.__check_permission_only(course)
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

    def __general_permission_check(self, course_id, ajax=False, no_redirect=False):
        if not self._check_login(ajax, no_redirect):
            return False

        course = self._get_course_by_id(course_id)                                   # 获取当前查看的课程
        if course is None:
            return False

        if not self.__check_permission(course, ajax, no_redirect):
            return False

        return course

    def new_course_message(self, course_id):
        """
        发布课程通知
        :param course_id:
        :return:
        """

        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        self._template_file = "education/manager/course_message_editor.html"
        self._context = {
            'type': "new",
            'course': course,
            "message": {
                "deadline": int(time.time()) + 86400 * 7
            }
        }

    def modify_course_message(self, course_id, message_id):
        """
        修改课程通知
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        messages = EduModel.CourseMessage.objects.filter(course=course, id=message_id)
        if not messages.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "未找到课程通知，返回列表请刷新"
            return

        self._template_file = "education/manager/course_message_editor.html"
        self._context = {
            'type': " modify",
            'course': course,
            "message": messages[0]
        }

    def save_new_course_message(self, course_id):
        """
        保存发布的课程通知
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        self._set_course_message(course)

    def save_modify_course_message(self, course_id, message_id):
        """
        保存发布的课程通知
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        messages = EduModel.CourseMessage.objects.filter(course=course, id=message_id)
        if not messages.exists():
            self._result = kernel.RESTStruct(False, '未找到课程通知')
            return

        self._set_course_message(course, messages[0])

    def _set_course_message(self, course, message=None):
        """
        课程通知设置模块
        :param course:
        :param message:
        :return:
        """
        content = self._request.POST.get('content', '')
        title = self._request.POST.get('title', '')
        if title.strip() == '':
            self._result = kernel.RESTStruct(False, '请输入通知标题')
            return False
        if content.strip() == '':
            self._result = kernel.RESTStruct(False, '请输入通知内容')
            return False
        try:
            deadline = self._request.POST.get('deadline', '')
            deadline = time.mktime(datetime.datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S").timetuple())
        except:
            self._result = kernel.RESTStruct(False, '时间格式错误')
            return False

        if message is not None:
            msg = message
        else:
            msg = EduModel.CourseMessage()
            msg.course = course
            msg.time = int(time.time())

        msg.title = title
        msg.content = content
        msg.deadline = deadline
        msg.save()

        self._result = kernel.RESTStruct(True)
        return True

    def delete_course_message(self, course_id, message_id):
        """
        删除课程通知
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        messages = EduModel.CourseMessage.objects.filter(course=course, id=message_id)
        if not messages.exists():
            self._result = kernel.RESTStruct(False, '未找到课程通知')
            return
        msg = messages[0]
        msg.delete()

        self._result = kernel.RESTStruct(True)

    def get_arrangement_signature(self, course_id, arrangement_id):
        """
        获取排课授权码
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        arrangement = course.arrangements.filter(id=arrangement_id)
        if not arrangement.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "找不到排课信息，请刷新页面返回"
            return
        arrangement = arrangement[0]

        signature = self._get_signature(arrangement.signature)
        print signature
        arrangement.signature = signature
        arrangement.save()

        self._template_file = "education/manager/ajax_signature.html"
        self._context = {
            'course': course,
            'signature': signature.split("|"),
            'arrangement': arrangement.toString()
        }

    def course_arrangement(self, course_id):
        """
        排课管理
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        arrangement = course.arrangements.all()

        self._template_file = "education/manager/course_arrangement.html"
        self._context = {
            'course': course,
            'arrangement_list': arrangement
        }

    def new_course_arrangement(self, course_id):
        """
        排课管理-新建排课信息
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        self._template_file = "education/manager/course_arrangement_editor.html"
        self._context = {
            'type': 'new',
            'course': course,
            'weeks': range(1,8),
            'weeks_term': range(1, 53),
            'sections': range(1, 14)
        }

    def modify_course_arrangement(self, course_id, arrangement_id):
        """
        排课管理-编辑排课信息
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        arrangement = course.arrangements.filter(id=arrangement_id)
        if not arrangement.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "找不到排课信息，请刷新页面返回"
            return

        self._template_file = "education/manager/course_arrangement_editor.html"
        self._context = {
            'type': 'modify',
            'course': course,
            'arrangement': arrangement[0],
            'weeks': range(1,8),
            'weeks_term': range(1, 53),
            'sections': range(1, 14)
        }

    def save_modify_course_arrangement(self, course_id, arrangement_id):
        """
        保存排课编辑信息
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        arrangement = course.arrangements.filter(id=arrangement_id)
        if not arrangement.exists():
            self._result = kernel.RESTStruct(False, '"找不到排课信息')
            return

        return self._set_course_arrangement(course, arrangement[0])

    def save_new_course_arrangement(self, course_id):
        """
        保存新建排课
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        return self._set_course_arrangement(course)

    def delete_course_arrangement(self, course_id, arrangement_id):
        """
        删除排课信息
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        arrangement = course.arrangements.filter(id=arrangement_id)
        if not arrangement.exists():
            self._result = kernel.RESTStruct(False, '"找不到排课信息')
            return
        arrangement = arrangement[0]
        arrangement.delete()

        self._result = kernel.RESTStruct(True)

    def _set_course_arrangement(self, course, arrangement=None):
        start_week = self._request.POST.get('start_week', '')
        end_week = self._request.POST.get('end_week', '')
        start_section = self._request.POST.get('start_section', '')
        end_section = self._request.POST.get('end_section', '')
        day_of_week = self._request.POST.get('day_of_week', '')
        start_time = self._request.POST.get('start_time', '')
        end_time = self._request.POST.get('end_time', '')
        odd_even = self._request.POST.get('odd_even', '')

        try:
            start_week = int(start_week)
            end_week = int(end_week)
            start_section = int(start_section)
            end_section = int(end_section)
            day_of_week = int(day_of_week)
            tmp = start_time.split(":")
            start_time = int(tmp[0])*3600 + int(tmp[1])*60
            tmp = end_time.split(":")
            end_time = int(tmp[0])*3600 + int(tmp[1])*60
            odd_even = int(odd_even)
        except:
            self._result = kernel.RESTStruct(False, '时间或数字格式错误，请检查')
            return

        if arrangement is None:
            arrangement = EduModel.Arrangement()
            arrangement.parent_course = course
            arrangement.teacher = self._user_session.entity
            arrangement.save()
            course.arrangements.add(arrangement)

        arrangement.start_week = start_week
        arrangement.end_week = end_week
        arrangement.start_section = start_section
        arrangement.end_section = end_section
        arrangement.day_of_week = day_of_week
        arrangement.start_time = start_time
        arrangement.end_time = end_time
        arrangement.odd_even = odd_even
        arrangement.save()

        self._result = kernel.RESTStruct(True)

    def course_student(self, course_id):
        """
        选课学生管理
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        arr_id = self._request.GET.get("arr_id", '')

        students = []

        if arr_id.strip() != '' and str.isdigit(str(arr_id)):
            arrangement = course.arrangements.filter(id=arr_id)
        else:
            arrangement = course.arrangements.all()

        if not arrangement.exists():
            arrangement = course.arrangements.all()

        for arr in arrangement:
            for stu in arr.students.all():
                students.append({
                    "arrid": arr.id,
                    "realname": stu.realname,
                    "id": stu.id,
                    "arrangement": arr.toString()
                })

        if not str.isdigit(str(arr_id)):
            arr_id = 0
        else:
            arr_id = int(arr_id)

        self._template_file = "education/manager/course_student.html"
        self._context = {
            'course': course,
            'students': students,
            'arr_id': arr_id,
            'arrangement': course.arrangements.all()
        }

    def change_course_students(self, course_id):
        """
        学生管理：更改排课信息
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        action_ids = self._request.POST.getlist("action_ids")       # 获取批量操作的列表
        if len(action_ids) == 0:
            self._result = kernel.RESTStruct(False, '请选择要操作的项目')
            return
        action = self._request.POST.get("action", '')               # 获取执行动作

        msg = []

        if str(action) == 'delete':                                 # 如果执行动作不是【删除】，则值为排课ID
            target_arr = None
        else:
            target_arr = course.arrangements.filter(id=action)      # 根据排课ID扫描排课信息
            if not target_arr.exists():                             # 值非法
                self._result = kernel.RESTStruct(False, '没有找到排课信息')
                return
            target_arr = target_arr[0]

        for ids in action_ids:
            id_temp = ids.split("|")
            if len(id_temp) != 2:
                continue
            arrid = id_temp[0]
            stuid = id_temp[1]
            student = AccountModel.User.objects.filter(id=stuid.strip(), role=1)       # 检查用户是否存在并且是否为学生用户
            if student.exists():
                student = student[0]
            else:                                                                       # 不存在则取消本次操作
                msg.append(u"学生 ID=%s 不存在" % stuid.strip())
                continue
            arr = course.arrangements.filter(id=arrid.strip())
            if arr.exists():
                arr = arr[0]
                arr.students.remove(student)                # 从排课列表中删除
            else:
                msg.append(u"排课信息 ID%s 不存在" % arrid.strip())
                continue

            if target_arr is not None:                                      # 向要移动到排课记录中添加学生信息，如果是删除操作，则不会执行到这里
                target_arr.students.add(student)

        if len(msg) == 0:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功")
        else:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功，但某些项目可能存在问题：<br />" + u"<br />".join(msg))

    def add_course_students(self, course_id):
        """
        学生管理：添加学生
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        arrid = self._request.POST.get('arrangement', "")
        if arrid.strip() == "":
            return
        arrangement = course.arrangements.filter(id=arrid)
        if not arrangement.exists():
            self._result = kernel.RESTStruct(False, '排课信息不存在')
            return
        arrangement = arrangement[0]

        msg = []

        files = self._request.FILES.get('upload_xls')
        if files is None:

            studentids = self._request.POST.get("new_studentids", "")  # 获取批量操作的列表
            if studentids.strip() == '':
                self._result = kernel.RESTStruct(False, '请输入要添加的学生学号')
                return
            studentids = studentids.split(",")

            for stuid in studentids:
                student = AccountModel.User.objects.filter(id=stuid.strip(), role=1)       # 检查用户是否存在并且是否为学生用户
                if student.exists():
                    student = student[0]
                else:                                                                       # 不存在则取消本次操作
                    msg.append(u"学生 ID=%s 不存在" % stuid.strip())
                    continue
                if arrangement.students.filter(id=stuid.strip()).exists():
                    continue
                else:
                    arrangement.students.add(student)
        else:
            path = "student_import_xls/%s%s" % (uuid.uuid4(), '.xls')
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
                    stu_id = user_row[0]
                    student = AccountModel.User.objects.filter(id=stu_id.strip(), role=1)  # 检查用户是否存在并且是否为学生用户
                    if student.exists():
                        student = student[0]
                        if arrangement.students.filter(id=stu_id.strip()).exists():
                            msg.append(u"学生 ID=%s 已选择当前排课" % stu_id.strip())
                            continue
                        else:
                            arrangement.students.add(student)
                    else:
                        msg.append(u"学生 ID=%s 不存在" % stu_id.strip())
            except:
                self._result = kernel.RESTStruct(False, u"XLS文件处理过程出现错误，请检查XLS文件是否填写正确")
                return

        arrangement.save()

        if len(msg) == 0:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功")
        else:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功，但某些项目可能存在问题：<br />" + u"<br />".join(msg))

    def course_editor(self, course_id=None):
        """
        新增/编辑课程
        :param course_id: 如果不设置则为新增
        :return:
        """
        course = None
        if course_id is not None:
            course = self.__general_permission_check(course_id, True, True)
            if course is False:
                return
        else:
            if self._user_session.user_role < 2:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "你没有权限创建课程"
                return

        teachers = []
        if self._user_session.user_role == 99:
            teachers = AccountModel.User.objects.filter(role=2)

        self._template_file = "education/manager/ajax_course_editor.html"
        self._context = {
            'course': course,
            'teachers': teachers,
            'departments': EduModel.EduDepartment.objects.all(),
            "year_terms": kernel.GeneralTools.get_year_terms()
        }

    def save_course_editor(self, course_id=None):
        """
        保存课程信息
        :param course_id: 如果不存在则新建
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = None
        if course_id is not None:
            course = self.__general_permission_check(course_id, True)
            if course is False:
                return
        else:
            if self._user_session.user_role < 2:
                self._result = kernel.RESTStruct(False, '你没有权限创建课程')
                return

        name = self._request.POST.get('name', '')
        department_id = self._request.POST.get('department', '')
        if name.strip() == '':
            self._result = kernel.RESTStruct(False, '请输入课程名称')
            return
        dep = None
        if department_id.strip() == '':
            self._result = kernel.RESTStruct(False, '请选择学院信息')
            return
        else:
            dep = EduModel.EduDepartment.objects.filter(id=department_id)
            if not dep.exists():
                self._result = kernel.RESTStruct(False, '学院信息不存在')
                return
            dep = dep[0]

        if course is None:
            year = self._request.POST.get("year", self._config.year)
            term = self._request.POST.get("term", self._config.term)
        else:
            year = self._request.POST.get("year", course.year)
            term = self._request.POST.get("term", course.term)

        try:
            year = int(year)
            term = int(term)
        except:
            self._result = kernel.RESTStruct(False, "学年学期数据有误！")
            return

        if self._user_session.user_role == 99:

            teacher_id = self._request.POST.get('teacher', '')
            if teacher_id.strip() == '':
                self._result = kernel.RESTStruct(False, '请选择教师')
                return

            teacher = AccountModel.User.objects.filter(id=teacher_id, role=2)
            if not teacher.exists():
                self._result = kernel.RESTStruct(False, '所选择教师不存在')
                return
            teacher = teacher[0]

        else:
            teacher = self._user_session.entity

        if course is None:
            course = EduModel.Course()

        self._request.session['edu_viewer_year'] = year
        self._request.session['edu_viewer_term'] = term

        course.teacher = teacher
        course.name = name
        course.year = year
        course.term = term
        course.department = dep
        course.save()

        self._result = kernel.RESTStruct(True, data=course.id)

    def course_delete(self, course_id):
        """
        删除课程信息
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        asgn_course = AsgnModel.Asgn.objects.filter(course=course).count()
        if asgn_course > 0:
            self._result = kernel.RESTStruct(False, '检测到当前课程存在作业信息，无法执行删除操作。')
            return
        course.delete()
        self._result = kernel.RESTStruct(True)

    def course_assistants(self, course_id):
        """
        助教管理
        :param course_id:
        :return:
        """
        course = self.__general_permission_check(course_id, True, True)
        if course is False:
            return

        assistants = course.assistants.all()

        self._template_file = "education/manager/course_assistants.html"
        self._context = {
            'course': course,
            'assistants': assistants,
            'arrangement': course.arrangements.all()
        }

    def add_course_assistants(self, course_id):
        """
        助教管理：添加助教
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        studentids = self._request.POST.get("new_studentids", "")       # 获取批量操作的列表
        if studentids.strip() == '':
            self._result = kernel.RESTStruct(False, '请输入要添加的助教学号')
            return
        studentids = studentids.split(",")

        msg = []

        for stuid in studentids:
            student = AccountModel.User.objects.filter(id=stuid.strip())       # 检查用户是否存在
            if student.exists():
                student = student[0]
            else:                                                              # 不存在则取消本次操作
                msg.append(u"学生 ID=%s 不存在" % stuid.strip())
                continue
            if course.assistants.filter(id=stuid.strip()).exists():
                msg.append(u"学生 ID=%s 已选择当前排课" % stuid.strip())
                continue
            else:
                course.assistants.add(student)

        course.save()

        if len(msg) == 0:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功")
        else:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功，但某些项目可能存在问题：<br />" + u"<br />".join(msg))

    def change_course_assistants(self, course_id):
        """
        助教管理：更改助教信息
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        action_ids = self._request.POST.getlist("action_ids")       # 获取批量操作的列表
        if len(action_ids) == 0:
            self._result = kernel.RESTStruct(False, '请选择要操作的项目')
            return

        msg = []

        for ids in action_ids:
            student = AccountModel.User.objects.filter(id=ids.strip())       # 检查用户是否存在并且是否为学生用户
            if student.exists():
                student = student[0]
                course.assistants.remove(student)               # Remove
            else:                                                                       # 不存在则取消本次操作
                msg.append(u"学生 ID=%s 不存在" % ids.strip())
                continue

        if len(msg) == 0:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功")
        else:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功，但某些项目可能存在问题：<br />" + u"<br />".join(msg))

    def enable_resource_repositories(self, course_id):
        """
        教学资料仓库管理：启用、关闭仓库
        :param course_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        course = self.__general_permission_check(course_id, True)
        if course is False:
            return

        rhandle = self._request.POST.getlist("rhandle")
        repo_list = course.repositories.all()
        exist_handles = []
        for repo in repo_list:
            exist_handles.append(repo.handle)

        msg = []

        for handle in rhandle:
            repo = EduModel.Repository.objects.filter(handle=handle)
            if not repo.exists():
                msg.append(u"仓库 handle=%s 不存在" % repo.handle.strip())
                continue
            repo = repo[0]
            if handle not in exist_handles:
                course.repositories.add(repo)
            else:
                exist_handles.remove(handle)

        for handle in exist_handles:
            repo = EduModel.Repository.objects.filter(handle=handle)
            if not repo.exists():
                msg.append(u"仓库 handle=%s 不存在" % repo.handle.strip())
                continue
            repo = repo[0]
            course.repositories.remove(repo)

        course.save()

        if len(msg) == 0:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功")
        else:
            self._result = kernel.RESTStruct(True, msg=u"批量操作成功，但某些项目可能存在问题：<br />" + u"<br />".join(msg))