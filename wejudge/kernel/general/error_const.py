# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

DEFAULT_WAIT_TIME = 4
NO_WATI_TIME = 0

DEFAULT_ACTION_JUMP = 0
DEFAULT_ACTION_HISTORY_GOBACK = 1

ALERT_LEVEL_SUCCESS = 'success'
ALERT_LEVEL_DANGER = 'danger'
ALERT_LEVEL_WARNING = 'warning'
ALERT_LEVEL_INFO = 'info'
ALERT_LEVEL_PRIMARY = 'primary'
ALERT_LEVEL_DEFAULT = 'default'


ERROR_WECHATAPI_UNKNOW_STATE = {
    'msg': '微信接口：未知的STATE参数',
    'code': 'wx05',
    'action': DEFAULT_ACTION_JUMP,
    'jump_url': '/',
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_WECHATAPI_USER_BINDED = {
    'msg': '当前微信已经绑定过OJ的账号，请检查是否有人盗用过您的账号或者是您先前是否在某个账号绑定过您的微信',
    'code': 'wx04',
    'jump_url': '/',
    'action': DEFAULT_ACTION_JUMP,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_WECHATAPI_PLEASE_LOGIN = {
    'msg': '请先登录您的OJ账户，再进行绑定过程',
    'code': 'wx03',
    'jump_url': '/',
    'action': DEFAULT_ACTION_JUMP,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_WECHATAPI_NEVER_BIND_ANY_USER = {
    'msg': '当前微信账户没有绑定网站账号，无法使用微信登录功能',
    'code': 'wx02',
    'jump_url': '/',
    'action': DEFAULT_ACTION_JUMP,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_WECHATAPI_USER_CANCEL_AUTH = {
    'msg': '微信授权过程被用户终止',
    'code': 'wx01',
    'jump_url': '/',
    'action': DEFAULT_ACTION_JUMP,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_WECHATAPI_UNKNOW_ERROR = {
    'msg': '微信接口调用失败',
    'code': 'wx00',
    'action': DEFAULT_ACTION_JUMP,
    'jump_url': '/',
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_ADMIN_PERMISSION_DENIED = {
    'msg': '当前账户没有操作权限',
    'code': 901,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_CONTEST_NOT_FOUND = {
    'msg': '比赛信息不存在',
    'code': 501,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_CONTEST_PERMISSION_DENIED = {
    'msg': '您没有权限访问当前比赛',
    'code': 502,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_CONTEST_ADMIN_PERMISSION_DENIED = {
    'msg': '您没有权限管理当前比赛',
    'code': 503,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_CONTEST_PROBLEM_NOT_FOUND = {
    'msg': '没有找到比赛指定的题目',
    'code': 504,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_CONTEST_NOT_START = {
    'msg': '比赛还没有开始',
    'code': 505,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_CONTEST_ENDED = {
    'msg': '比赛已经结束',
    'code': 506,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_CONTEST_FAQ_NOT_FOUND = {
    'msg': '未找到FAQ消息',
    'code': 507,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_CONTEST_VISIT_STATUS_AFTER_CONTEST_ENDED = {
    'msg': '您不能在比赛结束后访问比赛评测记录',
    'code': 508,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_CONTEST_NEW_REQUIRE_AGREEMENT = {
    'msg': '请先同意比赛服创建的相关条例',
    'code': 599,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_CONTEST_REQUIRE_TITLE = {
    'msg': '请输入比赛名称',
    'code': 598,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}



ERROR_DOCS_PERMISSION_DENIED = {
    'msg': '您没有权限访问当前课程的教学资料',
    'code': 401,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_DOCS_PATH_NOT_FOUND = {
    'msg': '当前教学资料目录不存在',
    'code': 404,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_EDU_CNOTICE_NOT_FOUND = {
    'msg': '课程公告不存在',
    'code': 402,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_EDU_COURSE_NOT_FOUND = {
    'msg': '未找到课程',
    'code': 403,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_EDU_REPO_NOT_FOUND = {
    'msg': '未能找到可用的教学资料仓库',
    'code': 404,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_ASGN_NOT_FOUND = {
    'msg': '没有找到这个作业',
    'code': 301,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_ASGN_PERMISSION_DENIED = {
    'msg': '您没有访问这个作业的权限',
    'code': 302,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_ASGN_TIMEOUT = {
    'msg': '当前作业提交时间未到或者已经过去，不能提交',
    'code': 303,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_ASGN_USER_REPORT_NOT_FOUND = {
    'msg': '当前用户在本次作业并没有生成过实验报告',
    'code': 304,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_ASGN_GROUP_NOT_FOUND = {
    'msg': '当前作业组不存在',
    'code': 305,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_ASGN_REPORT_NO_USE = {
    'msg': '当前用户不支持这个功能',
    'code': 306,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_PROBLEM_NOT_FOUND = {
    'msg': '当前问题不存在或被屏蔽',
    'code': 201,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_READ_JUDGE_RESULT_FAILED = {
    'msg': '抱歉，暂时无法读取判题结果数据',
    'code': 202,
    'action': DEFAULT_ACTION_JUMP,
    'jump_url': '/',
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_JUDGE_RESULT_ONLY_USER = {
    'msg': '抱歉，您没有权限访问此判题结果，或者出题者屏蔽了评测结果访问',
    'code': 203,
    'action': DEFAULT_ACTION_JUMP,
    'jump_url': '/',
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_LOAD_TDMAKER = {
    'msg': '加载题目测试数据失败',
    'code': 204,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_USER_NOT_FOUND = {
    'msg': '用户不存在',
    'code': 101,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}

ERROR_USER_ROLE_NO_USE_FUNC = {
    'msg': '您的账户角色不能访问此功能',
    'code': 102,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
ERROR_USER_SPECIAL_ACCOUNT = {
    'msg': '比赛专用账号不支持访问此功能',
    'code': 103,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}


ERROR_UNKNOW = {
    'msg': '未知错误',
    'code': 0,
    'action': DEFAULT_ACTION_HISTORY_GOBACK,
    'wait_time': DEFAULT_WAIT_TIME,
    'alert_level': ALERT_LEVEL_DANGER
}
