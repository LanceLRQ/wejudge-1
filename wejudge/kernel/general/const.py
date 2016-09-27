# -*- coding: utf-8 -*-
# coding:utf-8

JUDGE_SERVICE_API_SECERT = ''               # 判题机接口访问授权密钥

DATA_CENTER_API_SECERT = ''                 # 数据中心接口访问授权密钥（即将废弃）

EMAIL_SMTP_AUTH_CODE = ''                   # SMTP发信服务密码

EMAIL_SMTP_SENDER = ''                      # SMTP发信服务账号

EMAIL_SMTP_SERVER = ''                      # SMTP发信服务器（目前OJ使用的是QQ邮箱）

EMAIL_SMTP_DEBUG = True                     # SMTP调试模式

ACCOUNT_PASSWORD_SALT = ''                  # salt值(用于加密用户密码)

ACCOUNT_LOGIN_SESSION_KEY = 'logined_session'               # Session用于存储登陆状态的名称

ACCOUNT_LOGIN_SESSION_RETRY_TIME = 'login_retry_time'       # 登陆锁定计时器名称

ACCOUNT_LOGIN_COOKIE_TOKEN = 'logined_token'                # Cookie用于存储Token的名称

ACCOUNT_LOGIN_COOKIE_UID = 'logined_user'                   # Cookie用于存储User_ID的名称

ACCOUNT_LOGIN_EXPIRE_TIME = 86400 * 14                      # Token有效期, 默认14天

ACCOUNT_LOGIN_RETRY_TOTAL = 5                               # 允许重试密码次数

ACCOUNT_LOGIN_RETRY_WAIT_TIME = 120                         # 多次重试后锁定时间(120秒)

ACCOUNT_ROLE_NORMAL = 0        # 正常用户

ACCOUNT_ROLE_STUDENT = 1       # 学生用户

ACCOUNT_ROLE_TEACHER = 2       # 老师用户

ACCOUNT_ROLE_ADMIN = 99        # 管理员用户

WECHAT_APP_ID = ''                          # 微信登录模块使用的APP_ID

WECHAT_APP_SECERT = ''                      # 微信登录模块使用的APP_Secert

MAX_REPOSITORY_SIZE = 1073741824            # 默认库大小(单位：字节)

VIEW_ACTION_RENDER = 'render'
VIEW_ACTION_REDIRECT = 'redirect'
VIEW_ACTION_JSON = 'json'
VIEW_ACTION_LOGIN_REQUEST = 'login_request'
VIEW_ACTION_ERROR_PAGE = 'error_page'
VIEW_ACTION_DEFAULT = 'default'
VIEW_ACTION_DOWNLOAD = 'download'

VIEW_CONTENT_TYPE_JSON = 'json'
VIEW_CONTENT_TYPE_TEXT = 'text'
VIEW_CONTENT_TYPE_DEFAULT = 'redirect'


# 用户角色名称
ACCOUNT_ROLE = {
    0: u'用户',
    1: u'学生',
    2: u'教师',
    3: u'观察者老师',
    99: u'管理员'
}

# 用户角色称呼
ACCOUNT_ROLE_CALLED = {
    0: u'',
    1: u'同学',
    2: u'老师',
    3: u'老师',
    99: u''
}

PROBLEM_TESTDATA_DIR = '/data/data/testdatas'                       # 题目测试数据存放点 （nfs挂载为r）

PROGRAM_RUN_OUTDATAS_TEMP = '/data/data/temp'                       # 程序运行输出数据临时存放点 (nfs挂载为rw)

PROGRAM_RUN_OUTDATAS = '/data/data/judgeouts'                       # 程序运行输出数据存放点 (nfs不用挂载)

USER_UPLOADCODE_DIR = '/data/data/code_submits'                     # 用户上传代码数据存放点 （nfs挂载为r）

EDU_REPOSITORY_ROOT_DIR = '/data/data/resource/repositories'        # 课程资料库数据存放点 （nfs不挂载）

CKEDITOR_UPLOAD_IMAGE_DIR = '/data/data/resource/imgupload'         # CkEditor上传照片数据存放点 （nfs不挂载）

EXPORT_PROCESS_TEMP_DIR = '/data/data/resource/export_temp'         # 数据导出临时存放点 （nfs不挂载）

IMPORT_PROCESS_TEMP_DIR = '/data/data/resource/import_temp'         # 数据导入临时存放点 （nfs不挂载）

PUBLIC_DOWNLOAD_DIR = '/data/data/resource/download'                # 公共资源存放点 （nfs不挂载）

USER_HEADIMAGE_DIR = '/data/data/resource/headimg'                  # 用户头像位置

# =====评测支持======

JUDGEMENT_SOURCE_CODE_MAIN_FILENAME = 'main'

LANGUAGE_PROVIDE = ['gcc', 'gcc-cpp', 'java']

LANGUAGE_DESCRIPTION = {
    'gcc': 'GNU C',
    'gcc-cpp': 'GNU C++',
    'java': "Java"
}

SOURCE_CODE_EXTENSION = {
    'gcc': 'c',
    'gcc-cpp': 'cpp',
    'java': "java"
}

SIGNUM_DESC = {
    4: u'非法指令(SIGILL)',
    6: u'异常中止(SIGABRT/SIGIOT)',
    7: u'总线异常(SIGBUS)',
    8: u'浮点运算溢出(SIGFPE)，也有可能是除数为零等情况',
    9: u'强制进程终止(SIGKILL)，可能是因为程序时间或内存超限导致操作系统强制结束程序',
    11: u'非法内存地址引用(SIGSEGV)，可能是由数组越界、非法指针、内存超限等引发的',
    14: u'时钟中断(SIGALRM)',
    15: u'进程终止(SIGTERM)',
    16: u'协处理器栈错误(SIGSTKFLT)',
    24: u'CPU时间限制被打破(SIGXCPU)，也就是运行超时咯',
    25: u'文件大小限制被打破(SIGXFSZ)，系统输出限制为100MB，测试数据不可能太大的。',
    31: u'系统调用异常(SIGSYS/SYSUNUSED)',
}

PROBLEM_DIFFICULTY = {
    0: u'未分级',
    1: u'入门',
    2: u'简单',
    3: u'一般',
    4: u'较难',
    5: u'困难',
}

BG_IMAGES = [
    '1.jpg',
    '2.jpg',
    '3.jpg'
]

JUDGE_STATUS_FLAG_DESC = {
    -3: {
        'title': '未知',
        'en': 'Unknown',
        'color': 'default'
    },
    -2: {
        'title': '队列中',
        'en': 'Pending',
        'color': 'default'
    },
    -1: {
        'title': '评测中',
        'en': 'Judging',
        'color': 'default'
    },
    0: {
        'title': '评测通过(AC)',
        'en': 'Accepted',
        'color': 'success',
        'abbr': 'AC'
    },
    1: {
        'title': '格式错误(PE)',
        'en': 'Presentation Error',
        'color': 'warning',
        'abbr': "PE"
    },
    2: {
        'title': '超过时间限制(TLE)',
        'en': 'Time Limit Exceeded',
        'color': 'danger',
        'abbr': "TLE"
    },
    3: {
        'title': '超过内存限制(MLE)',
        'en': 'Memory Limit Exceeded',
        'color': 'danger',
        'abbr': "MLE"
    },
    4: {
        'title': '答案错误(WA)',
        'en': 'Wrong Answer',
        'color': 'danger',
        'abbr': "WA"
    },
    5: {
        'title': '运行时错误(RE)',
        'en': 'Runtime Error',
        'color': 'danger',
        'abbr': "RE"
    },
    6: {
        'title': '输出内容超限(OLE)',
        'en': 'Output Limit Exceeded',
        'color': 'danger',
        'abbr': "OLE"
    },
    7: {
        'title': '编译失败(CE)',
        'en': 'Compile Error',
        'color': 'info',
        'abbr': "CE"
    },
    8: {
        'title': '系统错误(SE)',
        'en': 'System Error',
        'color': 'danger',
        'abbr': "SE"
    },
    9: {
        'title': '等待重判',
        'en': 'Pending Rejudge',
        'color': 'default'
    },
    20: {
        'title': '等待人工评判',
        'en': 'Pending Manual Judge',
        'color': 'default'
    }
}
