# -*- coding: utf-8 -*-
# coding:utf-8
import wejudge.apps.problem.models as ProblemMdl
import wejudge.apps.asgn.models as AsgnModel
import wejudge.kernel.general as kernel

__author__ = 'lancelrq'


class ProblemArchive(kernel.ViewerFramework):
    """题目库提供类"""

    def __init__(self, request):
        kernel.ViewerFramework.__init__(self, request)
        self._navbar_action = 'problem'

    def list_archive(self, page=1, limit=20):
        """
        题库列表
        :param page: 分页信息
        :param limit: 每页显示数量
        :return:
        """

        if self._user_session.is_logined() and not self._user_session.preference_problem_detail_mode:
            limit = 100

        pv_info = None
        pdata = None

        classify_id = self._request.GET.get("classify_id", 0)
        try:
            classify_id = int(classify_id)
        except:
            classify_id = 0

        keyword = self._request.GET.get('keyword', '')
        author_type = self._request.GET.get('author_type', '')
        author_id = self._request.GET.get('author_id', '')
        diff = self._request.GET.get('diff', '')
        desc = self._request.GET.get('desc', '0')
        if desc.strip() == '1':
            desc = True
        else:
            desc = False
        if diff is not None and diff.strip() == '':
            diff = -1
        else:
            try:
                diff = int(diff)
            except:
                diff = -1
            finally:
                if diff < -1 or diff > 5:
                    diff = -1
        author = "%s%s" % (author_type, author_id)

        if self._user_session.is_logined() and self._user_session.user_role in [2, 3, 99]:
            pda = ProblemArchiveQuery.list_archive(classify_id, keyword, author, True, desc, diff)
        else:
            pda = ProblemArchiveQuery.list_archive(classify_id, keyword, author, False, desc, diff)

        count = pda.count()

        if count == 0:
            pager_render = ''
        else:
            pager = kernel.PagerProvider(count, limit, page, "problem_archive", 11, _get=self._request.GET)
            pdata = pda.all()[pager.start_idx: pager.start_idx + limit]
            pager_render = pager.render()
            if self._user_session.is_logined():
                pv_info = ProblemArchiveQuery.get_my_problem_visited_record(pdata, self._user_session.entity)
            else:
                pv_info = {}

        # asgn_id = self._request.GET.get("asgn_id", None)
        #
        # if asgn_id is None:
        #     asgn_id = self._request.session.get("problem_archive_choosing_to_asgn", 0)
        #     try:
        #         asgn_id = int(asgn_id)
        #     except:
        #         asgn_id = 0
        #     if asgn_id == 0:                            # 非选课模式
        #         asgn_id = ""
        # else:
        #     try:
        #         asgn_id = int(asgn_id)
        #         if asgn_id < 0:
        #             asgn_id = 0
        #     except:
        #         asgn_id = 0
        #
        #     if asgn_id == 0:                            # 退出选课模式
        #         self._request.session["problem_archive_choosing_to_asgn"] = 0
        #         asgn_id = ""
        #     else:
        #         self._request.session["problem_archive_choosing_to_asgn"] = asgn_id

        asgn_id = self._request.GET.get("asgn_id", '')
        if asgn_id != "" and asgn_id != 0 and asgn_id != '0':
            self._user_session.entity.preference_problem_detail_mode = False
            asgn = AsgnModel.Asgn.objects.filter(id=asgn_id)
            if asgn.exists():
                asgn = asgn[0]
            else:
                asgn_id = ""
                asgn = None
        else:
            asgn_id = ""
            asgn = None

        self._template_file = 'problem/archive/list.html'
        self._context = {
            'pager': pager_render,
            'problems': pdata,
            'problem_visited': pv_info,
            'asgn_id': asgn_id,
            'asgn_choosing': asgn,
            "classify_id": 0 if classify_id < 0 else classify_id,
            # filter:
            'keyword': keyword,
            'author_id': author_id,
            'author_type': author_type,
            'desc': "1" if desc else "0",
            'diff': diff
        }
        pass

    def get_filter_page(self):
        """
        获取过滤器列表
        :return:
        """
        keyword = self._request.GET.get('keyword', '')
        author_type = self._request.GET.get('author_type', '')
        author_id = self._request.GET.get('author_id', '')
        diff = self._request.GET.get('diff', '')
        desc = self._request.GET.get('desc', '')
        asgn_id = self._request.GET.get('asgn_id', '')

        if str(desc.strip()) == '1':
            desc = True
        else:
            desc = False
        if diff is not None and diff.strip() == '':
            diff = -1
        else:
            try:
                diff = int(diff)
            except:
                diff = -1
            finally:
                if diff < -1 or diff > 5:
                    diff = -1
        self._template_file = "problem/archive/filter.html"
        kernel.const.JUDGE_STATUS_FLAG_DESC.iteritems()
        self._context = {
            "keyword": keyword,
            "author_id": author_id,
            "author_type": author_type,
            "diff": diff,
            'desc': desc,
            "difficulty": kernel.const.PROBLEM_DIFFICULTY.iteritems(),
            "asgn_id": asgn_id
        }


class ProblemArchiveQuery(object):

    @staticmethod
    def list_archive(classify_id=0, keyword=None, author_id=None, show_all=False, desc=False, diff=-1):
        """
        获取评测列表
        :param classify_id: 分类列表
        :param keyword: 关键字(标题）
        :param author_id: 作者
        :param show_all: 显示全部
        :param desc: 倒序排序
        :param diff: 题目难度
        :return:
        """

        if classify_id > 0:
            cids = list(set(ProblemArchiveQuery.get_children_nodes(classify_id)))
            pda = ProblemMdl.Problem.objects.filter(classify__in=cids).distinct()
        elif classify_id == -1:
            pda = ProblemMdl.Problem.objects.filter(classify=None)
        else:
            pda = ProblemMdl.Problem.objects.filter()

        if not show_all:
            pda = pda.filter(is_show=True, pre_verify=None)

        if diff > -1:
            pda = pda.filter(difficulty=diff)

        if (author_id is not None) and (author_id.strip() != ""):
            if author_id[:3] == '[n]':
                pda = pda.filter(author__nickname=author_id[3:])
            elif author_id[:3] == '[r]':
                pda = pda.filter(author__realname=author_id[3:])
            else:
                pda = pda.filter(author__id=author_id)

        if (keyword is not None) and (keyword.strip() != ""):
            pda = pda.filter(title__contains=keyword)

        if desc:
            pda = pda.order_by('-id')

        return pda

    @staticmethod
    def get_children_nodes(parent_id):
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
            cids.extend(ProblemArchiveQuery.get_children_nodes(node.id))
        return cids

    @staticmethod
    def get_my_problem_visited_record(problems, author):
        pv_info = {}
        for problem in problems:
            pv = ProblemMdl.ProblemVisited.objects.filter(problem=problem, author=author)
            if pv.exists():
                pv = pv[0]
                pv_info[problem.id] = {
                    "total": pv.submissions,
                    "ac": pv.accepted,
                    'ratio': kernel.GeneralTools.ratio(pv.accepted, pv.submissions)
                }
        return pv_info
