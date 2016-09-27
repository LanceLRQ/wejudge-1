# -*- coding: utf-8 -*-
# coding:utf-8

import json
import time
import uuid
import hashlib
import wejudge.apps.problem.models as ProblemMdl
import wejudge.kernel.general as kernel
import ProblemBody as PBInc

__author__ = 'lancelrq'


class ProblemManager(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'problem'

    # === 鉴权 ===

    def __check_permission_only(self, problem=None, owner_only=False):
        """
        检查权限
        :param problem: 问题记录
        :param owner_only: 仅允许拥有者操作（管理员无效）
        :return:
        """
        if self._user_session.user_role == 99:
            return True
        elif self._user_session.user_role == 2:
            if problem is None:
                return True
            # 判断题目为当前用户拥有
            if self._user_session.user_id == problem.author.id:
                return True
            else:
                if not owner_only:
                    return False if problem.disable_edit_by_other else True
                else:
                    return False
        else:
            return False

    def __check_permission(self, problem=None, ajax=False, owner_only=False, no_redirect=False):
        """
        检查权限（包含渲染数据处理，也就是说调用完的结果为False时只要return即可，不必再写渲染代码）
        :param problem: 问题记录
        :ajax problem: 是否为ajax请求
        :param owner_only: 仅允许拥有者操作（管理员无效）
        :param no_redirect: 禁用错误页面跳转
        :return:
        """
        flag = self.__check_permission_only(problem, owner_only)
        if flag is False:
            if no_redirect:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "[ERROR]当前账户没有操作权限"
                return flag
            if ajax:
                self._action = kernel.const.VIEW_ACTION_JSON
                self._result = kernel.RESTStruct(False, u'当前账户没有操作权限')
                return flag
            else:
                self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
                self._context = kernel.error_const.ERROR_ADMIN_PERMISSION_DENIED
                return flag
        return flag

    # === 功能 ===

    def batch_change_visiable(self, flag):
        # 改变题目的可见性接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        if int(flag) == 0:
            vflag = False
        else:
            vflag = True

        problem_ids = self._request.POST.getlist('problem_ids')
        ps = ProblemMdl.Problem.objects.filter(id__in=problem_ids)

        msg = []

        for p in ps:
            if self.__check_permission_only(p, owner_only=True):
                p.is_show = vflag
                p.save()
            else:
                msg.append("%s.%s" % (p.id, p.title))
        if len(msg) > 0:
            self._result = kernel.RESTStruct(True, msg="操作成功，但是以下项目没有改动：<br />%s" % "<br />".join(msg))
        else:
            self._result = kernel.RESTStruct(True, msg="操作成功")

    def save_classify_to_problem(self, classify_id=0):
        """
        将题目移动到某分类
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        if int(classify_id) > 0:
            node = ProblemMdl.ProblemClassify.objects.filter(id=classify_id)
            if not node.exists():
                self._result = kernel.RESTStruct(False, "分类不存在")
                return
            node = node[0]
        else:
            node = None

        problem_ids = self._request.POST.getlist('problem_ids')
        ps = ProblemMdl.Problem.objects.filter(id__in=problem_ids)

        msg = []

        for p in ps:
            if self.__check_permission_only(p, owner_only=True):
                p.classify = node
                p.save()
            else:
                msg.append("%s.%s" % (p.id, p.title))

        if len(msg) > 0:
            self._result = kernel.RESTStruct(True, msg="操作成功，但是以下项目没有改动：<br />%s" % "<br />".join(msg))
        else:
            self._result = kernel.RESTStruct(True, msg="操作成功")

    def new_problem(self):
        # 新建题目页面
        if not self._check_login():
            return
        if not self.__check_permission():
            return
        self._template_file = "problem/manager/new_problem.html"

    def modify_problem(self, pid):
        # 题目修改页面
        if not self._check_login():
            return
        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_PROBLEM_NOT_FOUND
            return
        if not self.__check_permission(problem):
            return
        tq = ProblemMdl.TdmakerQueue.objects.filter(problem=problem).order_by("-id")
        if tq.count() > 30:
            tq = tq[:30]
        self._template_file = "problem/manager/problem_mgr.html"
        self._context = {
            "problem": problem,
            "test_data": problem.test_data.order_by("order"),
            "tdmaker_queue": tq
        }

    def save_new_problem(self):
        # 保存新建题目接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return
        if not self.__check_permission(None, True):
            return

        rel, msg = self.__save_problem_setting()
        if rel:
            self._result = kernel.RESTStruct(rel, data=msg)
        else:
            self._result = kernel.RESTStruct(rel, msg)

    def save_problem_infomation(self, pid):
        # 保存题目基础信息接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, ajax=True, owner_only=True):
            return

        rel, msg = self.__save_problem_setting(problem)
        self._result = kernel.RESTStruct(rel, msg)

    def save_problem_demo_code(self, pid):
        # 保存题目的示例代码接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        code_content = self._request.POST.get('content')
        code_lang = self._request.POST.get('lang')

        if not kernel.const.LANGUAGE_DESCRIPTION.has_key(code_lang):
            self._result = kernel.RESTStruct(False, msg='不支持的评测语言')
            return

        problem.demo_code = json.dumps({
            "lang": code_lang,
            "content": code_content
        })
        problem.save()
        self._result = kernel.RESTStruct(True)

    def change_problem_judge_pause(self, pid, pause):
        # 设置题目的评测启动或停止
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        if pause == '1':
            pause = True
        else:
            pause = False

        if pause is False and problem.test_data.count() == 0:
            self._result = kernel.RESTStruct(False, '当前题目没有测试数据，无法启动评测')
            return

        problem.pause_judge = pause
        problem.save()

        self._result = kernel.RESTStruct(True)

    def delete_problem(self, pid):
        # 删除题目接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        confrim = self._request.POST.get('confrim', '0')
        if str(confrim) != '1':
            self._result = kernel.RESTStruct(False, '请先阅读并且同意此操作需要承担的风险')
            return

        problem.delete()
        self._result = kernel.RESTStruct(True)

    def run_tdmaker(self, pid):
        # 运行测试数据生成器
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        demo_code = {}
        if problem.demo_code is not None and problem.demo_code.strip() != "":
            demo_code = json.loads(problem.demo_code)
        lang = demo_code.get('lang', 'gcc')

        que = ProblemMdl.TdmakerQueue()
        que.author = self._user_session.entity
        que.problem = problem
        que.lang = lang
        que.flag = -1
        que.save()

        self._result = kernel.RESTStruct(True)

    def testdata_view(self, pid, handle):
        # 查看测试数据
        if not self._check_login(ajax=True, no_redirect=True):
            return
        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到题目信息"
            return
        if not self.__check_permission(problem, no_redirect=True):
            return
        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到测试数据信息"
            return
        td = testdata[0]

        stor = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(problem.id))
        if stor.get_file_size("%s.in" % str(td.handle)) < 1048576:
            tdin = stor.read_file("%s.in" % str(td.handle))
        else:
            tdin = None
        if stor.get_file_size("%s.out" % str(td.handle)) < 1048576:
            tdout = stor.read_file("%s.out" % str(td.handle))
        else:
            tdout = None

        if tdin is None or tdout is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR] 测试数据过大，请考虑通过上传下载来处理"
        else:
            try:
                if tdin is not None:
                    tdin = tdin.encode("utf-8")
            except:
                tdin = '(数据加载失败，请勿点击保存按钮以防数据覆盖)'
            try:
                if tdout is not None:
                    tdout = tdout.encode("utf-8")
            except:
                tdout = '(数据加载失败，请勿点击保存按钮以防数据覆盖)'
            self._template_file = "problem/manager/testdata_view.html"
            self._context = {
                "td": td,
                "problem": problem,
                "in": tdin,
                "out": tdout
            }

    def testdata_setting(self, pid, handle):
        # 修改测试数据设置
        if not self._check_login(ajax=True, no_redirect=True):
            return
        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到题目信息"
            return
        if not self.__check_permission(problem, no_redirect=True, owner_only=True):
            return
        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到测试数据信息"
            return
        self._template_file = "problem/manager/testdata_setting.html"
        self._context = {
            "td": testdata[0],
            "problem": problem
        }

    def save_testdata_setting(self, pid):
        # 保存测试数据设置接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(ajax=True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        handle = self._request.POST.get('handle', '')
        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._result = kernel.RESTStruct(False, '未找到测试数据信息')
            return

        name = self._request.POST.get('name', '')
        order = self._request.POST.get('order', '')
        visible = self._request.POST.get('visible', '')
        available = self._request.POST.get('available', '')

        if name.strip() == '':
            self._result = kernel.RESTStruct(False, '请输入名称')
            return
        if order.strip() == '':
            self._result = kernel.RESTStruct(False, '请输入顺序编号')
            return
        if visible == '1':
            visible = True
        else:
            visible = False
        if available == '1':
            available = True
        else:
            available = False

        try:
            order = int(order)
        except:
            self._result = kernel.RESTStruct(False, '顺序编号错误')
            return

        testdata = testdata[0]
        testdata.name = name
        testdata.available = available
        testdata.visible = visible
        testdata.order = order
        testdata.save()

        self._result = kernel.RESTStruct(True)

    def delete_testdata(self, pid, handle):
        # 删除测试数据接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(ajax=True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._result = kernel.RESTStruct(False, '未找到测试数据信息')
            return

        td = testdata[0]
        stor = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(problem.id))
        stor.delete("%s.in" % str(td.handle))
        stor.delete("%s.out" % str(td.handle))
        td.delete()

        if problem.test_data.count() == 0:
            problem.pause_judge = True
            problem.save()

        self._result = kernel.RESTStruct(True)

    def new_testdata(self, pid):
        # 新建测试数据接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(ajax=True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        order = problem.test_data.count() + 1

        td = ProblemMdl.TestData()
        td.handle = kernel.GeneralTools.get_my_handle_id()
        td.name = "Problem %s Testdata %d" % (str(problem.id), order)
        td.order = order
        td.available = True
        td.visible = False
        td.update_time = 0
        td.save()

        stor = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(problem.id))
        stor.new_file("%s.in" % str(td.handle), '')
        stor.new_file("%s.out" % str(td.handle), '')

        problem.test_data.add(td)

        self._result = kernel.RESTStruct(True)

    def save_testdata_view(self, pid):
        # 保存测试数据内容的接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(ajax=True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        handle = self._request.POST.get('handle', '')
        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._result = kernel.RESTStruct(False, '未找到测试数据信息')
            return

        tdin = self._request.POST.get('in', '').replace("\r\n", '\n').replace("\r", "\n")
        tdout = self._request.POST.get('out', '').replace("\r\n", '\n').replace("\r", "\n")

        if tdin == u"(数据加载失败，请勿点击保存按钮以防数据覆盖)":
            self._result = kernel.RESTStruct(False, '防覆盖保护')
            return
        if tdout == u"(数据加载失败，请勿点击保存按钮以防数据覆盖)":
            self._result = kernel.RESTStruct(False, '防覆盖保护')
            return

        stor = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(problem.id))
        stor.new_file("%s.in" % str(handle), tdin)
        stor.new_file("%s.out" % str(handle), tdout)

        self._result = kernel.RESTStruct(True)

    def testdata_download(self, pid, handle, filetype='in'):
        # 测试数据下载接口
        self._action = kernel.const.VIEW_ACTION_DEFAULT

        if not self._check_login(ajax=True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到题目信息"
            return

        if not self.__check_permission(problem, True):
            return

        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到测试数据信息"
            return

        td = testdata[0]
        self._action = kernel.const.VIEW_ACTION_DOWNLOAD
        self._context = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(problem.id))
        self._template_file = "%s.%s" % (str(td.handle), filetype)
        self._download_filename = "%s.%s" % (str(td.name), filetype)

    def testdata_upload(self, pid, handle):
        # 上传测试数据
        if not self._check_login(ajax=True, no_redirect=True):
            return
        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到题目信息"
            return
        if not self.__check_permission(problem, no_redirect=True, owner_only=True):
            return
        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "[ERROR]未找到测试数据信息"
            return
        self._template_file = "problem/manager/testdata_upload.html"
        self._context = {
            "td": testdata[0],
            "problem": problem
        }

    def testdata_upload_api(self, pid, handle):
        # 测试数据上传接口
        self._action = kernel.const.VIEW_ACTION_JSON

        if not self._check_login(ajax=True):
            return

        query = PBInc.ProblemBodyQuery()
        problem = query.get_problem_detail(pid, True)
        if problem is None:
            self._result = kernel.RESTStruct(False, '题目信息未找到')
            return

        if not self.__check_permission(problem, True, owner_only=True):
            return

        testdata = problem.test_data.filter(handle=handle)
        if not testdata.exists():
            self._result = kernel.RESTStruct(False, '未找到测试数据信息')
            return

        td = testdata[0]
        try:
            file_in = self._request.FILES.get('uploadFileIn', None)
            file_out = self._request.FILES.get('uploadFileOut', None)
            th = td.handle

            stor = kernel.LocalStorage(kernel.const.PROBLEM_TESTDATA_DIR, str(problem.id))

            if file_in is not None:
                if file_in.size > 16*1024*1024:
                    self._result = kernel.RESTStruct(False, u'上传文件过大！')
                    return
                fp = stor.open_file("%s.in" % th, 'wb+')
                for chunk in file_in.chunks():
                    fp.write(chunk)
                fp.close()
                self._clear_BOM(stor, "%s.in" % th)

            if file_out is not None:
                if file_out.size > 16*1024*1024:
                    self._result = kernel.RESTStruct(False, u'上传文件过大！')
                    return
                fp = stor.open_file("%s.out" % th, 'wb+')
                for chunk in file_out.chunks():
                    fp.write(chunk)
                fp.close()
                self._clear_BOM(stor, "%s.out" % th)

            self._result = kernel.RESTStruct(True)
        except BaseException, ex:
            self._result = kernel.RESTStruct(False, msg="上传数据保存错误(%s)" % str(ex))

    # === 私有功能 ===

    def _clear_BOM(self, td_stor, fn):
        fp = td_stor.open_file(fn, 'rb')
        if "\xef\xbb\xbf" == fp.read(3):
            contents = fp.read()
            fp.close()
            fp = td_stor.open_file(fn, 'wb')
            fp.write(contents)
            fp.close()
            return
        fp.close()

    def __save_problem_setting(self, problem=None):

        title = self._request.POST.get('title', None)
        difficulty = self._request.POST.get('difficulty', 0)

        description = self._request.POST.get('description', None)
        input = self._request.POST.get('input', None)
        output = self._request.POST.get('output', None)
        sample_input = self._request.POST.get('sample_input', None)
        sample_output = self._request.POST.get('sample_output', None)
        hint = self._request.POST.get('hint', '')
        source = self._request.POST.get('source', '')
        c_time_limit = self._request.POST.get('c_time_limit', 1000)
        java_time_limit = self._request.POST.get('java_time_limit', 1000)
        c_memory_limit = self._request.POST.get('c_memory_limit', 32768)
        java_memory_limit = self._request.POST.get('java_memory_limit', 32768)
        disable_edit_by_other = self._request.POST.get('disable_edit_by_other', '')
        is_private = self._request.POST.get('is_private', '')

        is_private = True if is_private == '1' else False
        disable_edit_by_other = True if disable_edit_by_other == '1' else False

        if (title is None) or (title.strip() == ''):
            return False, u"请输入题目的标题"
        if (description is None) or (description.strip() == ''):
            return False, u"请输入题目的描述内容"
        if (input is None) or (input.strip() == ''):
            input = '无'
        if (output is None) or (output.strip() == ''):
            return False, u"请输入题目的输出描述"
        if (sample_input is None) or (sample_input.strip() == ''):
            sample_input = ''
        if (sample_output is None) or (sample_output.strip() == ''):
            return False, u"请输入题目的输出样例"
        if not str.isdigit(str(c_time_limit)) or not str.isdigit(str(java_time_limit)):
            return False, u"限制时间必须是一个数字"
        if not str.isdigit(str(c_memory_limit)) or not str.isdigit(str(java_memory_limit)):
            return False, u"限制内存大小必须是一个数字"

        c_time_limit = int(c_time_limit)
        java_time_limit = int(java_time_limit)
        c_memory_limit = int(c_memory_limit)
        java_memory_limit = int(java_memory_limit)

        if c_time_limit < 1000 or c_time_limit > 60000:
            return False, u'C/C++语言评测的时间应在1s-60s之间'
        if java_time_limit < 2000 or java_time_limit > 60000:
            return False, u'Java语言评测的时间应在2s-60s之间'
        if c_memory_limit < 32768 or c_memory_limit > 262144:
            return False, u'C/C++语言评测的内存控制应在32MB-256MB之间'
        if java_memory_limit < 256000 or java_memory_limit > 524288:
            return False, u'Java语言评测的内存控制应在256MB-512MB之间'

        if problem is None:
            problem = ProblemMdl.Problem()
            problem.create_time = int(time.time())
            problem.author = self._user_session.entity

        problem.title = title
        problem.update_time = int(time.time())
        problem.difficulty = difficulty
        problem.description = description
        problem.input = input
        problem.output = output
        problem.sample_input = sample_input
        problem.sample_output = sample_output
        problem.hint = hint
        problem.source = source

        problem.c_time_limit = c_time_limit
        problem.c_memory_limit = int(c_memory_limit)
        problem.java_time_limit = int(java_time_limit)
        problem.java_memory_limit = int(java_memory_limit)

        problem.is_private = is_private
        problem.disable_edit_by_other = disable_edit_by_other

        problem.save()
        return True, problem.id
