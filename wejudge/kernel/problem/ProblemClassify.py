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


class ProblemClassify(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'problem'

    # === 鉴权 ===

    def __check_permission_only(self, classify=None):
        """
        检查权限
        :param classify: 问题记录
        :return:
        """
        if self._user_session.user_role == 99:
            return True
        elif self._user_session.user_role == 2:
            if classify is None:
                return True
            # 判断题目为当前用户拥有
            if self._user_session.user_id == classify.author.id:
                return True
            else:
                p = classify.parent
                while p is not None:
                    if p.author.id == self._user_session.user_id:
                        return True
                    else:
                        p = p.parent
                return False
        else:
            return False

    def __check_permission(self, classify=None, ajax=False, no_redirect=False):
        """
        检查权限（包含渲染数据处理，也就是说调用完的结果为False时只要return即可，不必再写渲染代码）
        :param classify: 分类记录
        :param ajax: 是否为ajax请求
        :param no_redirect: 禁用错误页面跳转
        :return:
        """
        flag = self.__check_permission_only(classify)
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

    # === 功能 ===

    def get_classify_list(self, now_id=None):
        """
        获取分类信息
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_DEFAULT
        id = self._request.GET.get("id", 0)
        try:
            id = int(id)
        except:
            id = 0

        if now_id is not None:
            now_id = int(now_id)
            node = ProblemMdl.ProblemClassify.objects.filter(id=now_id)
            parent_list = []
            data_list = []
            if node.exists():
                node = node[0]
                p = node.parent                 # 获取当前节点的父节点
                while p is not None:                  # 如果不是根节点
                    parent_list.append(p.id)
                    p = p.parent

            data_list = self._get_classify_list_data(parent_list, now_id)

            data_list = [{
                "id": "0",
                "text": "显示全部",
                "children": data_list,
                "state": {
                    "opened": True,
                    "selected": True if now_id == 0 else False
                }
            }]

            self._context =json.dumps(data_list)

        else:
            if id != 0:
                clist = ProblemMdl.ProblemClassify.objects.filter(parent__id=id)
            else:
                clist = ProblemMdl.ProblemClassify.objects.filter(parent=None)
            data = []
            for classify in clist:
                if ProblemMdl.ProblemClassify.objects.filter(parent__id=classify.id).exists():
                    no_extend = True
                else:
                    no_extend = False
                data.append({
                    "id": classify.id,
                    "text": classify.title,
                    "children": no_extend
                })
            self._context =json.dumps(data)

    def _get_classify_list_data(self, parent_list, now_id, parent_id=None):
        """
        递归展开列表
        :param parent_list:
        :param parent_id:
        :return:
        """
        data_list = []
        no_extend = None
        clist = ProblemMdl.ProblemClassify.objects.filter(parent__id=parent_id)
        for node in clist:
            if (node.id in parent_list) or node.id == now_id:
                tmp = self._get_classify_list_data(parent_list, now_id, node.id)
                opened = True
            else:
                if ProblemMdl.ProblemClassify.objects.filter(parent__id=node.id).exists():
                    tmp = True
                else:
                    tmp = False
                opened = False
            if now_id == node.id:
                selected = True
            else:
                selected = False
            data_list.append({
                "id": str(node.id),
                "text": node.title,
                "children": tmp,
                "state": {
                    "opened": opened,
                    "selected": selected
                }
            })
        return data_list

    def classify_editor(self, classify_id=0, is_new=False):
        """
        增加、修改分类
        :param classify_id:
        :param is_new: 是否为增加
        :return:
        """
        if not self._check_login():
            return
        if is_new is False and int(classify_id) == 0:
            self._action = kernel.const.VIEW_ACTION_DEFAULT
            self._context = "根分类不能被编辑"
            return
        if int(classify_id) > 0:
            node = ProblemMdl.ProblemClassify.objects.filter(id=classify_id)
            if node.exists():
                node = node[0]
                if node.author.id == self._user_session.user_id:
                    editable = True
                else:
                    editable = False
                    p = node.parent
                    while p is not None:
                        if p.author.id == self._user_session.user_id:
                            editable = True
                            break
                        else:
                            p = p.parent
            else:
                self._action = kernel.const.VIEW_ACTION_DEFAULT
                self._context = "[ERROR]未找到节点"
                return
        else:
            editable = False
            node = None

        self._template_file = "problem/classify/editor.html"
        self._context = {
            "is_new": is_new,
            "editable": editable,
            "node": node,
            "id": int(classify_id)
        }

    def classify_selector(self):
        """
        分类选择器
        :return:
        """
        classify_id = self._request.GET.get("classify_id", "0")
        try:
            classify_id = int(classify_id)
        except:
            classify_id = 0
        if int(classify_id < 0):
            classify_id = 0
        self._template_file = "problem/classify/selector.html"
        self._context = {
            "classify_id": classify_id
        }

    def save_classify_editor(self, classify_id=0, is_new=False):
        """
        增加、修改分类的处理程序
        :param classify_id:
        :param is_new:是否为增加
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login():
            return
        if is_new is False:
            if int(classify_id) == 0:
                self._result = kernel.RESTStruct(False, "根分类不能被编辑")
                return
        else:
            if self._user_session.user_role < 2:
                self._result = kernel.RESTStruct(False, "当前账户没有操作权限")
                return
        if int(classify_id) == 0 and is_new:
            node = None
        else:
            node = ProblemMdl.ProblemClassify.objects.filter(id=classify_id)
            if not node.exists():
                self._result = kernel.RESTStruct(False, "未找到节点")
                return
            node = node[0]
            if not self.__check_permission(node, True):
                return

        title = self._request.POST.get("title", "")
        if title.strip() == "":
            self._result = kernel.RESTStruct(False, "请输入分类标题")
            return

        if is_new:
            if node is not None:
                cnt = 1
                p = node.parent
                while p is not None:
                    cnt += 1
                    p = p.parent
                if cnt >= 3:
                    self._result = kernel.RESTStruct(False, "当前分类最大深度为3，不可创建子分类")
                    return
            new_node = ProblemMdl.ProblemClassify()
            new_node.author = self._user_session.entity
            new_node.parent = node
            new_node.title = title
            new_node.save()
        else:
            node.title = title
            node.save()

        self._result = kernel.RESTStruct(True)

    def delete_classify(self, classify_id=0):
        """
        删除分类
        :param classify_id:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login():
            return
        if int(classify_id) == 0:
            self._result = kernel.RESTStruct(False, "根分类不能被删除")
            return
        node = ProblemMdl.ProblemClassify.objects.filter(id=classify_id)
        if not node.exists():
            self._result = kernel.RESTStruct(False, "未找到节点")
            return
        node = node[0]
        if not self.__check_permission(node, True):
            return

        cids = list(set(self.get_children_nodes(node.id)))
        plist = ProblemMdl.Problem.objects.filter(classify__in=cids)
        for p in plist:
            p.classify = None
            p.save()

        node.delete()
        self._result = kernel.RESTStruct(True)

    def get_children_nodes(self, parent_id):
        """
        递归取得所有子节点
        :param parent_id:
        :return:
        """
        cids = [parent_id]
        clist = ProblemMdl.ProblemClassify.objects.filter(parent_id=parent_id)
        cids.append(parent_id)
        for node in clist:
            cids.append(node.id)
            cids.extend(self.get_children_nodes(node.id))
        return cids