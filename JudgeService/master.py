# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'


import os
import json
import time
import logging
import lorun
import base64
import random
import MySQLdb
import config as Config
import base as Base
import master_func as Function

safeExit = False
lastActiveTime = -1


# 队列获取模块
def get_judge_queue_item():

    conn = Base.dbManager.getConn()
    try:
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        result = cursor.execute('SELECT * FROM `problem_judgequeue` WHERE `queue_status` = 0 OR `queue_status` = -1 ORDER BY `queue_status` DESC, `id` ASC LIMIT 1')
        if result > 0:
            res = cursor.fetchone()
            id = res.get('id')
            sid = res.get('judge_status_id', 0)
            queue_status = res.get('queue_status', 0)
            if queue_status == -1:
                Base.log("[JudgeService]****重判队列****")
            cursor.execute('UPDATE `problem_judgequeue` SET `queue_status` = 1 WHERE `id` = %s', (str(id),))
            conn.commit()
            cursor.execute('UPDATE `problem_judgestatus` SET `flag` = -1 WHERE `id` = %s', (str(sid),))
            conn.commit()
            cursor.close()
            conn.close()
            return id, sid
        else:
            cursor.close()
            conn.close()
            return None, ''
    except BaseException, ex:
        conn.rollback()
        conn.close()
        return None, str(ex)


# 队列回滚模块
def rollback_judge_queue_item(qid):
    conn = Base.dbManager.getConn()
    try:
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE `problem_judgequeue` SET `queue_status` = 0 WHERE `id` = %s', (str(qid),))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    except BaseException, ex:
        conn.rollback()
        conn.close()
        return False


# 业务逻辑
def work():
    try:
        global lastActiveTime
        lastActiveTime = -1
        # 1. 从数据库队列获取新的评测请求
        queue_id, status_id = get_judge_queue_item()
        if queue_id is not None:
            # 2. 读取评测状态的详情
            judge_options = Base.api(Config.API_GET_JUDGE_LIST_ITEM % str(status_id))
            if judge_options is False:
                Base.log('[JudgeService]获取评测状态信息失败，或者，稍后将重试。(LOAD_STATUS_INFO_ERROR)', logging.ERROR)
                t = rollback_judge_queue_item(queue_id)
                if t:
                    Base.log('[JudgeService]队列操作成功回滚。(QUEUE_ROLLBACK_FINISHED)')
                else:
                    Base.log('[JudgeService]队列操作回滚失败。(QUEUE_ROLLBACK_FAILED)', logging.ERROR)
                return

            lastActiveTime = int(time.time())
            lang = str(judge_options.get('lang', ''))
            Base.log('[JudgeService]获取队列成功，ID：%s，评测语言：%s(JUDGEMENT_LOAD_QUEUE)' % (str(status_id), lang))
            # 3.执行评测
            rel = Function.main(judge_options)
            # 4.报告评测结果
            apirel = Base.api(Config.API_JUDGE_RESULT_RECEICER % str(status_id), {'result': json.dumps(rel)})
            if apirel is not False:
                Base.log('[JudgeService]评测成功结束。(JUDGE_FINISHED)')
            else:
                t = rollback_judge_queue_item(queue_id)
                if t:
                    Base.log('[JudgeService]队列操作成功回滚。(QUEUE_ROLLBACK_FINISHED)')
                else:
                    Base.log('[JudgeService]队列操作回滚失败。(QUEUE_ROLLBACK_FAILED)', logging.ERROR)

        else:
            if status_id is None:
                Base.log('[JudgeService]获取队列信息失败，稍后将重试。(GET_QUEUE_ERROR)\n[问题描述：%s]' % str(status_id), logging.ERROR)
            return

    except BaseException, ex:
        Base.log('[JudgeService]评测机业务逻辑发生错误(WORK_RUNTIME_ERROR)\n[问题描述：%s]' % str(ex), logging.ERROR)
        return
