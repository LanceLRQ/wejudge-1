# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import os
import json
import time
import lorun
import base64
import random
import MySQLdb
import config as Config
import base as Base
import logging
import tdmaker_func as Function

safeExit = False
lastActiveTime = -1


# 队列获取模块
def get_judge_queue_item():

    conn = Base.dbManager.getConn()
    try:
        cursor = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)
        result = cursor.execute('SELECT * FROM `problem_tdmakerqueue` WHERE `queue_status` = 0 ORDER BY `id` ASC LIMIT 1')
        if result > 0:
            res = cursor.fetchone()
            id = res.get('id')
            cursor.execute('UPDATE `problem_tdmakerqueue` SET `queue_status` = 1 WHERE `id` = %s', (str(id),))
            conn.commit()
            cursor.close()
            conn.close()
            return id
        else:
            cursor.close()
            conn.close()
            return None
    except BaseException, ex:
        conn.rollback()
        conn.close()
        return None, str(ex)


# 业务逻辑
def work():
    try:
        global lastActiveTime
        lastActiveTime = -1
        # 1. 从数据库队列获取新的评测请求
        queue_id = get_judge_queue_item()
        if queue_id is not None:
            # 2. 读取评测状态的详情
            judge_options = Base.api(Config.TDmakerAPI_GET_JUDGE_LIST_ITEM % str(queue_id))
            if judge_options is False:
                Base.log('[TDMaker]获取评测状态信息失败。(LOAD_STATUS_INFO_ERROR)', logging.ERROR)

            lastActiveTime = int(time.time())
            lang = str(judge_options.get('lang', ''))
            Base.log('[TDMaker]获取队列成功，ID：%s，评测语言：%s(JUDGEMENT_LOAD_QUEUE)' % (str(queue_id), lang))
            # 3.执行评测
            rel = Function.main(judge_options)
            # 4.报告评测结果
            apirel = Base.api(Config.TDmakerAPI_JUDGE_RESULT_RECEICER % str(queue_id), {'result': json.dumps(rel)})
            if apirel is not False:
                Base.log('[TDMaker]评测成功结束。(JUDGE_FINISHED)')

    except BaseException, ex:
        Base.log('[TDMaker]评测机业务逻辑发生错误(WORK_RUNTIME_ERROR)\n[问题描述：%s]' % str(ex), logging.ERROR)
        return
