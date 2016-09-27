# -*- coding: utf-8 -*-
# coding:utf-8
import os
import time
import threading
import base as Base
import master as Judge
import tdmaker as TdMaker
os.setuid(1000)

__author__ = 'lancelrq'

def JudegService():
    Base.log("[Judgement]评测机服务已经启动！")
    while (True and (not Judge.safeExit)):
        Judge.work()
        time.sleep(1)
    Base.log("评测服务...[OK]")


def tdmaker():
    Base.log("[TDMaker]测试数据生成器服务已经启动！")
    while True and (not TdMaker.safeExit):
        TdMaker.work()
        time.sleep(3)
    Base.log("测试数据生成器服务...[OK]")


if __name__ == '__main__':

    print("=========================\nWeJudge Judge Service\nVersion: 0.9.0a\n=========================")

    judge_thread = threading.Thread(target=JudegService)
    judge_thread.setDaemon(True)
    judge_thread.start()
    tdmaker_thread = threading.Thread(target=tdmaker)
    tdmaker_thread.setDaemon(True)
    tdmaker_thread.start()

    while True:
        time.sleep(1)
        pass
"""
        cmd = raw_input("")
        if (cmd == 'stop') or (cmd == 'close') or (cmd == 'exit') or (cmd == 'quit') or (cmd == 'q') or (cmd == 'e'):
            Judge.safeExit = True
            TdMaker.safeExit = True
            Base.log("[SYSTEM]正在关闭评测机服务...")
            judge_thread.join()
            tdmaker_thread.join()
            Base.log("[SYSTEM]评测服务成功关闭！再会！")
            break
        else:
            Base.log("[SYSTEM]评测机控制命令未知，请输入'help'获取支持的命令。")
"""
