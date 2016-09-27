# -*- coding: utf-8 -*-
# coding:utf-8
import django.core.urlresolvers
import hashlib
import uuid
import wejudge.apps.education.models as EduModel
import wejudge.kernel.general as kernel
__author__ = 'lancelrq'


class EducationRepositories(kernel.ViewerFramework):

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'education'
        pass

    # === 鉴权 ===

    def __check_permission_only(self, repo=None):
        """
        检查权限
        :param course: repo记录
        :return:
        """
        if self._user_session.user_role == 99:
            return True
        elif self._user_session.user_role == 2:
            # 判断题目为当前用户拥有
            if self._user_session.user_id == repo.author.id:
                return True
            else:
                return False
        else:
            return False

    def __check_permission(self, repo=None, ajax=False, no_redirect=False):
        """
        检查权限（包含渲染数据处理，也就是说调用完的结果为False时只要return即可，不必再写渲染代码）
        :param course: 课程记录
        :ajax problem: 是否为ajax请求
        :param owner_only: 仅允许拥有者操作（管理员无效）
        :param no_redirect: 禁用错误页面跳转
        :return:
        """
        flag = self.__check_permission_only(repo)
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

    def __general_permission_check(self, repo, ajax=False, no_redirect=False):
        """
        通用权限检查
        :param repo_handle:
        :param ajax:
        :param no_redirect:
        :return:
        """
        if not self._check_login(ajax, no_redirect):
            return False

        if not self.__check_permission(repo, ajax, no_redirect):
            return False

        return repo

    def _get_repository(self, handle=None):
        """
        获取仓库数据
        :param handle: 仓库Handle
        :return:
        """
        if handle is not None:
            repo = EduModel.Repository.objects.filter(handle=handle)
            if repo.exists():
                return repo[0]
            else:
                return None
        else:
            return None

    def _get_repository_detail(self, handle, path):
        """
        读取仓库文件列表
        :param handle:
        :return:
        """
        if handle is None:
            return None
        stor = kernel.LocalStorage(kernel.const.EDU_REPOSITORY_ROOT_DIR, handle)
        return {
            "dirs": stor.get_dirs_list(path),
            "files": stor.get_files_list(path, with_info=True)
        }

    def repository_index(self, handle=None):
        """
        仓库主页
        :param handle:
        :return:
        """
        if not self._check_login():
            return

        if self._user_session.user_role == 2:
            repo_list = EduModel.Repository.objects.filter(author=self._user_session.entity)
        elif self._user_session.user_role == 99:
            repo_list = EduModel.Repository.objects.all()
        else:
            repo_list = None
        repo = self._get_repository(handle)

        if repo_list is None and repo is None:                  # 如果不是教师、管理用户，并且没有找到仓库
            self._action = kernel.const.VIEW_ACTION_ERROR_PAGE
            self._context = kernel.error_const.ERROR_EDU_REPO_NOT_FOUND
            return
        # if repo is None and repo_list is not None and repo_list.exists():        # 如果没找到目标仓库，但账号是教师用户，并且找到了他创建的一个仓库
        #     self._action = kernel.const.VIEW_ACTION_REDIRECT
        #     self._redirect_url = django.core.urlresolvers.reverse("education_repository_index", args=(repo_list[0].handle,))
        #     return
        path = self._request.GET.get("path", "")
        self._template_file = "education/resource.html"
        self._context = {
            "repo_list": repo_list,
            "repository": repo,
            "content_list": self._get_repository_detail(handle, path) if handle is not None else None,
            "path": path
        }

    def change_repository(self, repo_handle=None):
        """
        新建、修改仓库
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role < 2:
            self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            return

        repo_name = self._request.POST.get("repo_name", "")
        if repo_name.strip() == "":
            self._result = kernel.RESTStruct(False, '请输入仓库的名称')
            return

        if repo_handle is None:
            handle = kernel.GeneralTools.get_my_handle_id()
            ok = False
            while not ok:
                repo = EduModel.Repository.objects.filter(handle=handle)
                if not repo.exists():
                    ok = True
            repo = EduModel.Repository()
            repo.handle = handle
            repo.author = self._user_session.entity
            repo.max_size = kernel.const.MAX_REPOSITORY_SIZE
        else:
            repo = self._get_repository(repo_handle)
            if repo is None:
                self._result = kernel.RESTStruct(False, '找不到仓库')
                return
            if not self.__general_permission_check(repo, True):
                return

        repo.title = repo_name
        repo.save()

        self._result = kernel.RESTStruct(True)

    def delete_repository(self, repo_handle=None):
        """
        删除仓库
        :param repo_handle:
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role < 2:
            self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            return
        repo = self._get_repository(repo_handle)
        if repo is None:
            self._result = kernel.RESTStruct(False, '找不到仓库')
            return
        if not self.__general_permission_check(repo, True):
            return

        repo.delete()
        stor = kernel.LocalStorage(kernel.const.EDU_REPOSITORY_ROOT_DIR, '')
        stor.delete(repo_handle)
        self._result = kernel.RESTStruct(True)

    def repository_upload_file(self, repo_handle):
        """
        上传文件
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role < 2:
            self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            return

        repo = self._get_repository(repo_handle)
        if repo is None:
            self._result = kernel.RESTStruct(False, '找不到仓库')
            return
        if not self.__general_permission_check(repo, True):
            return

        path = self._request.POST.get("path", "").replace("../", "").replace("..", "")
        stor = kernel.LocalStorage(kernel.const.EDU_REPOSITORY_ROOT_DIR, repo_handle)

        if not stor.exists(path):
            self._result = kernel.RESTStruct(False, '上传位置的文件夹不存在')
            return

        try:
            files = self._request.FILES.get('uploadFile', None)
            if files is None:
                self._result = kernel.RESTStruct(False, '无文件上传！')
                return

            if files.size == 0:
                self._result = kernel.RESTStruct(False, '无文件上传！')
                return

            if files.size > 1024*1024*1024:
                self._result = kernel.RESTStruct(False, '由于服务器硬盘空间大小限制，需要上传超过1G的文件请于管理员联系！')
                return

            file_name = "%s/%s" % (path, files.name.encode('utf-8'))

            destination = stor.open_file(file_name, "wb+")
            for chunk in files.chunks():
                destination.write(chunk)
            destination.close()

            self._result = kernel.RESTStruct(True)

        except BaseException, ex:
            self._result = kernel.RESTStruct(False, u'上传数据保存错误(%s)' % str(ex))

    def repository_new_folder(self, repo_handle):
        """
        新建文件夹
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role < 2:
            self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            return

        repo = self._get_repository(repo_handle)
        if repo is None:
            self._result = kernel.RESTStruct(False, '找不到仓库')
            return
        if not self.__general_permission_check(repo, True):
            return

        stor = kernel.LocalStorage(kernel.const.EDU_REPOSITORY_ROOT_DIR, repo_handle)
        path = self._request.POST.get("path", "").replace("../", "").replace("..", "")
        stor = stor.get_child_dir_storage(path)
        print stor.get_current_path()
        folder_name = self._request.POST.get("folder_name", "")

        if folder_name.strip() == "":
            self._result = kernel.RESTStruct(False, '请输入新文件夹名')
            return
        stor.new_folder(folder_name)
        self._result = kernel.RESTStruct(True)


    def repository_delete_files(self, repo_handle):
        """
        删除仓库内的文件或文件夹
        :return:
        """
        self._action = kernel.const.VIEW_ACTION_JSON
        if not self._check_login(True):
            return
        if self._user_session.user_role < 2:
            self._result = kernel.RESTStruct(False, '当前账户没有操作权限')
            return

        repo = self._get_repository(repo_handle)
        if repo is None:
            self._result = kernel.RESTStruct(False, '找不到仓库')
            return
        if not self.__general_permission_check(repo, True):
            return

        path = self._request.GET.get("path", "").replace("../", "").replace("..", "")
        stor = kernel.LocalStorage(kernel.const.EDU_REPOSITORY_ROOT_DIR, repo_handle)
        stor.delete(path)
        self._result = kernel.RESTStruct(True)
