# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'


SOURCE_CODE_EXTENSION = {
    'gcc': 'c',
    'gcc-cpp': 'cpp',
    'java': "java"
}

SOURCE_CODE_COMPILE_CMD = {
    'gcc': 'gcc %s -o %s -ansi -fno-asm -Wall -std=c99 -lm',
    'gcc-cpp': 'g++ %s -o %s -ansi -fno-asm -Wall -lm --static',
    'java': 'javac -encoding utf-8 -d %s %s'
}

JUDGE_SERVICE_API_SECERT = ''               # 判题机接口访问授权密钥（同 wejudge.kernel.general.const 内的常量)

LOG_FILE = '/data/wejudge/judge.log'                            # 日志文件

PROBLEM_TESTDATA_DIR = '/data/data/testdatas'                   # 测试数据存放文件夹

USER_UPLOADCODE_DIR = '/data/data/code_submits'                 # 提交代码存放文件夹

TEMP_PROGRAM_STORAGE = '/data/data/temp'                        # 评测工作临时文件夹

OJ_HOST = '127.0.0.1:6666'

API_GET_JUDGE_LIST_ITEM = 'http://' + OJ_HOST + '/problem/judge/api/get_problem_judge_options/%s'

API_JUDGE_RESULT_RECEICER = 'http://' + OJ_HOST + '/problem/judge/api/receive_judge_result/%s'

TDmakerAPI_GET_JUDGE_LIST_ITEM = 'http://' + OJ_HOST + '/problem/tdmaker/api/get_problem_judge_options/%s'

TDmakerAPI_JUDGE_RESULT_RECEICER = 'http://' + OJ_HOST + '/problem/tdmaker/api/receive_judge_result/%s'

RESULT_STR = [
    'Accepted',
    'Presentation Error',
    'Time Limit Exceeded',
    'Memory Limit Exceeded',
    'Wrong Answer',
    'Runtime Error',
    'Output Limit Exceeded',
    'Compile Error',
    'System Error'
]

MYSQL_CONFIG = {
    'NAME': 'wejudge',
    'USER': 'root',                     # 数据库账号
    'PASSWORD': '',                     # 数据库密码
    'HOST': '127.0.0.1',
    'PORT': 3306,
}
