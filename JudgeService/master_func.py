# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import os
import json
import uuid
import shutil
import lorun
import hashlib
import commands
import config as Config
import base as Base
import logging

# 唯一标识符
def uuidstr():
    uuid1 = uuid.uuid1()
    md5 = hashlib.md5()
    md5.update(str(uuid1))
    return md5.hexdigest()[8:-8]


# 编译代码方法
def execCompile(session_path, src_path, lang):
    Base.log('[JudgeService]编译程序 (JUDGE_COMPILING)')
    # 获取编译程序临时文件名
    if str(lang) == 'java':
        # 将提交的代码重命名为Main.java
        scname = os.path.join(session_path, "Main.java")
        shutil.copy(src_path, scname)
        src_path = scname
        # 编译
        ccmd = Config.SOURCE_CODE_COMPILE_CMD.get(lang)
        exitcode, output = commands.getstatusoutput(ccmd % (session_path, src_path))
    else:
        output_exec = os.path.join(session_path, "m")
        # 根据评测语言获取编译命令
        ccmd = Config.SOURCE_CODE_COMPILE_CMD.get(lang)
        # 运行编译并截取编译器返回的数据
        exitcode, output = commands.getstatusoutput(ccmd % (src_path, output_exec))

    # 判断是否正确编译
    if exitcode != 0:
        print output
        return False, output
    return True, None


# 评测运行方法
def execRunOnce(session_path, handel, config, td_in_path, td_out_path):
    my_out_filename = "%s.outdata" % handel
    # 获取程序运行结果输出文件的绝对路径
    tMP_PATH = os.path.join(session_path, my_out_filename)
    # 只读打开测试数据输入样例文件
    fin = open(td_in_path)
    # 清理遗留文件
    if os.path.exists(tMP_PATH):
        os.remove(tMP_PATH)
    # 只写打开运行结果文件
    ftemp = open(tMP_PATH, 'w+')
    # 创建评测配置信息
    # java -classpath <session_path> Main
    if str(config.get('lang')) == 'java':
        args = ['java', '-client', '-Dfile.encoding=utf-8', '-classpath', session_path, "Main"]

    else:
        args = [os.path.join(session_path, "m")]
    time_limit = config.get('time_limit', 1000)
    memory_limit = config.get('memory_limit', 32768)
    runcfg = {
        'args': args,  # 运行程序文件
        'fd_in': fin.fileno(),
        'fd_out': ftemp.fileno(),
        'timelimit': time_limit,
        'memorylimit': memory_limit
    }
    Base.log('[JudgeService]运行源程序！(JUDGE_PROCESS_START)')
    # 执行Lorun模块，运行程序
    rst = lorun.run(runcfg)
    Base.log('[JudgeService]程序运行结束！(JUDGE_PROCESS_FINISHED)')
    # 释放文件
    fin.close()
    ftemp.close()

    # 读取运行结果，0表示运行正常结束
    if int(rst.get('result', 0)) == 0:
        # 只读打开运行结果文件
        ftemp = open(tMP_PATH, 'r')
        # 只读打开测试数据输出样例文件
        fout = open(td_out_path)
        Base.log('[JudgeService]正在检查输出！(JUDGE_DATA_CHECK)')
        # 调用Lorun的检查模块检查答案错误
        crst = lorun.check(fout.fileno(), ftemp.fileno())
        Base.log('[JudgeService]输出检查完毕！(JUDGE_DATA_CHECK_FINISHED)')
        # 释放文件
        fout.close()
        ftemp.close()

        # 如果数据检查出错，返回结果
        if crst != 0:
            return {
                'result': crst,
                'memoryused': rst.get('memoryused', 0),
                'timeused': rst.get('timeused', 0)
            }, my_out_filename

    # 未通过，或者数据检查通过，都会运行到这里
    return rst, my_out_filename


def execJudge(session_path, config, pid, sid, testdatas):

    # 这是用来判断TLE计数的，因为判题机核心是按每次每个测试数据来给时间，但我是按总计来给时间的
    timeuseTotal = 0
    # 最大内存使用
    memuseMax = 0
    # 最大时间限制
    TIMELIMIT = config.get('time_limit', 10000)
    results = {}
    outdatas = {}

    testdatas.sort(key=lambda obj: obj.get('order'))

    for td in testdatas:
        # 取得测试数据UUID
        tdid = td.get('handle', None)
        tname = td.get('name', None)
        # 测试数据错误System Error
        if tdid is None:
            return results, 8, 0, 0, ''
        # 测试数据是否有效
        if td.get('available', True) is False:
            continue
        Base.log('[JudgeService]运行测试数据：%s[%s]  (TEST_DATA_VIEW)' % (str(tdid), str(tname)))
        inFile = os.path.join(Config.PROBLEM_TESTDATA_DIR, "%s/%s.in" % (str(pid), str(tdid)))
        outFile = os.path.join(Config.PROBLEM_TESTDATA_DIR, "%s/%s.out" % (str(pid),  str(tdid)))
        # 测试数据文件是否存在
        if os.path.exists(inFile) and os.path.exists(outFile):
            # 执行评测
            (crst, outdata) = execRunOnce(session_path, tdid, config, inFile, outFile)
            # 保存评测结果
            results[tdid] = crst
            # 保存运行输出
            outdatas[tdid] = outdata
            # 统计时间
            timeuseTotal += int(crst.get('timeused', 0))
            # 获取最大内存使用
            mem = crst.get('memoryused', 0)
            if mem > memuseMax:
                memuseMax = mem
            # 如果任意测试数据出错，则终止评测，返回当前评测结果
            if crst.get('result') != 0:
                return results, crst.get('result'), timeuseTotal, memuseMax, outdatas
            # 超时终止评测，返回评测结果
            if timeuseTotal > TIMELIMIT:
                return results, 2, timeuseTotal, memuseMax, outdatas  # TLE
        else:
            # 测试数据文件不存在，SE
            return None, 8, 0, 0, ''

    # 评测全部通过
    return results, 0, timeuseTotal, memuseMax, outdatas


# 评测入口
def main(judge_option):
    problem_id =judge_option.get('problem_id')
    status_id =judge_option.get('status_id')
    session_id = uuidstr()   # 评测Session
    session_path = os.path.join(Config.TEMP_PROGRAM_STORAGE, session_id)
    if not os.path.isdir(session_path):
        os.mkdir(session_path)
    # 编译代码
    source_code = "%s/%s" % (Config.USER_UPLOADCODE_DIR, judge_option.get('code_path'))
    flag, msg = execCompile(session_path, source_code, judge_option.get('lang'))
    if not flag:
        Base.log('[JudgeService]编译错误！(COMPILE_ERROR)', logging.ERROR)
        return {"exitcode": 7, 'ce_info': msg}  # Compile Error
    # 读取测试数据列表
    test_data = judge_option.get('test_data', None)
    if (test_data is None) or (isinstance(test_data, dict)):
        Base.log('[JudgeService]载入测试数据配置信息错误！(问题ID：%s)(LOAD_TEST_DATA_FAILED)' % str(problem_id), logging.ERROR)
        return {"exitcode": 8}  # System Error
    # 执行评测
    (result, exitcode, timeuse, memuse, outdatas) = execJudge(session_path, judge_option, problem_id, status_id, test_data)

    try:
        if str(judge_option.get('lang')) == 'java':
            os.remove(os.path.join(session_path, "Main.class"))
            os.remove(os.path.join(session_path, "Main.java"))
        else:
            os.remove(os.path.join(session_path, "m"))
    except:
        pass

    # 返回评测结果
    return {
        'outdatas': outdatas,
        "result": result,
        "exitcode": exitcode,
        'timeused': timeuse,
        'memused': memuse,
        'session_id': session_id
    }
