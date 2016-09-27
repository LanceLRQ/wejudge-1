# -*- coding: utf-8 -*-
# coding:utf-8
__author__ = 'lancelrq'

import os
import json
import time
import urllib
import urllib2
import MySQLdb
import config as Config
from DBUtils.PooledDB import PooledDB
import logging
import hashlib
import random

logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(threadName)s]%(levelname)s: %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename=Config.LOG_FILE,
)

class DbManager:

    def __init__(self):
        connkwargs = {
            'host': Config.MYSQL_CONFIG['HOST'],
            'user': Config.MYSQL_CONFIG['USER'],
            'port': Config.MYSQL_CONFIG['PORT'],
            'passwd': Config.MYSQL_CONFIG['PASSWORD'],
            'db': Config.MYSQL_CONFIG['NAME'],
            'charset': "utf8"
        }
        self._pool = PooledDB(MySQLdb, mincached=0, maxcached=10, maxshared=10, maxusage=10000, **connkwargs)

    def getConn(self):
        return self._pool.connection()

dbManager = DbManager()

def api(url, data=None):
    try:
        datasend = None
        if data is not None:
            datasend = urllib.urlencode(data)
        t, r, s = api_license()
        # log("t=%s, r=%s, s=%s" % (t, r, s))
        req = urllib2.Request(url + "?timestamp=%s&randstr=%s&signature=%s" % (t, r, s), datasend)
        resp = urllib2.urlopen(req)
        body = resp.read()
        data = json.loads(body)
        if data.get('flag', False):
            return data.get('data')
        else:
            log("[JudgeService]接口调用出错：%s(API_ERROR)" % data.get('msg'), logging.ERROR)
            return False
    except urllib2.HTTPError, ex:
        fp = open("./err_resp.html", "w+")
        fp.write(ex.read())
        fp.close()
        log("[JudgeService]接口网络访问失败(NATWORK_ERROR)", logging.ERROR)
        return False


def api_license():
    """
    接口访问权限生成器
    :return:
    """
    timestamp = str(int(time.time()))
    randstr = str("".join(random.sample(['0', '1', '2', '3', '4','5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'], 6)))
    secert = [
        Config.JUDGE_SERVICE_API_SECERT,               # 判题机接口访问授权密钥,
        timestamp,
        randstr
    ]
    secert.sort()       # 字典序
    secert = hashlib.sha256("".join(secert)).hexdigest()
    return timestamp, randstr, secert


def log(msg, level=logging.INFO):
    body = "[%s] %s" % (time.strftime("%m-%d %H:%M:%S"), msg)
    print body
    logging.log(level, msg)
