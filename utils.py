# -*- coding: utf-8 -*-

import gevent
import gevent.monkey
gevent.monkey.patch_all()
import signal, functools
import subprocess
import re
import time
from datetime import datetime, timedelta
import os
import sys
import hashlib
import requests
import urllib3
urllib3.disable_warnings()
import fake_useragent
import pymysql
import logging
import config

# 超时装饰器
class TimeoutError(Exception): pass  # 定义一个超时错误类

def timeout(seconds, error_msg='TIME_OUT_ERROR:Already Timeout!'):
    def decorated(func):
        result = ''
        def signal_handler(signal_num, frame):
            global result
            result = error_msg
            raise TimeoutError(error_msg)

        def wrapper(*args, **kwargs):
            global result
            signal.signal(signal.SIGALRM, signal_handler)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
                return result
        return functools.wraps(func)(wrapper)

    return decorated


# logutils
LOG_DIR = "../log/"
def get_logger(supplier, type):
    logger = logging.getLogger(supplier + "_" + type + "")
    logger.setLevel(logging.DEBUG)
    filename = LOG_DIR + supplier + "_" + type + ".log"
    handler = logging.FileHandler(filename=filename)
    # handler.setLevel(logging.DEBUG)
    _format = "%(asctime)s - " + supplier + "-" + type + "-->:%(message)s"
    formatter = logging.Formatter(_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# dbutils
class DB:

    def __init__(self, user, password, dbname, host="localhost", port=3306,
                 charset="utf8", autocommit=True):
        self.user = user
        self.password = password
        self.dbname = dbname
        self.host = host
        self.port = port
        self.charset = charset
        self.autocommit = autocommit
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = pymysql.connect(host=self.host, port=self.port,
                                    user=self.user, password=self.password,
                                    database=self.dbname, charset=self.charset)
        self.conn.autocommit(self.autocommit)

    def execute(self, sql):
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql)
        except Exception:
            self.close()
            self.connect()
            cursor = self.conn.cursor()
            cursor.execute(sql)
        return cursor

    def close(self):
        self.conn.close()

def get_db_local(autocommit=True):
    db = DB(user=config.db_username, password=config.db_password, dbname=config.db_name)
    db.connect()
    return db


# tunnelutils
class GetTunnel:
    def __init__(self):
        self.supplier_tunnel_dict = {
            "abuyun": self.abuyun_tunnel(),
            "kuaidaili": self.kuaidaili_tunnel(),
            "xiongmao": self.xiongmao_tunnel(),
            "xiaoxiang": self.xiaoxiang_tunnel(),
            "mogu": self.mogu_tunnel(),
            "wuyou": self.wuyou_tunnel(),
            "xundaili": self.xundaili_tunnel()
        }

    def get_tunnel(self, supplier):
        return self.supplier_tunnel_dict[supplier]

    def kuaidaili_tunnel(self):
        tunnel = config.kuaidaili_tunnel
        username = config.kuaidaili_username
        password = config.kuaidaili_password
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
        }
        headers = {
            'User-Agent': fake_useragent.UserAgent().random
        }
        return proxies, headers

    def xiongmao_tunnel(self):
        orderno = config.xiongmao_orderno
        secret = config.xiongmao_secret
        ip_port = config.xiongmao_tunnel
        timestamp = str(int(time.time()))  # 计算时间戳
        txt = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
        md5_string = hashlib.md5(txt.encode()).hexdigest()  # 计算sign
        sign = md5_string.upper()  # 转换成大写
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp + "&change=true"
        proxies = {
            "http": "http://" + ip_port,
            "https": "htts://" + ip_port
        }
        headers = {
            "Proxy-Authorization": auth,
            "User-Agent": fake_useragent.UserAgent().random
        }
        return proxies, headers

    def abuyun_tunnel(self):
        # 代理服务器
        tunnel = config.abuyun_tunnel
        proxyUser = config.abuyun_username
        proxyPass = config.abuyun_password
        proxyMeta = "http://%(user)s:%(pass)s@%(tunnel)s" % {"user": proxyUser, "pass": proxyPass, "tunnel": tunnel}
        proxies = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        headers = {
            'User-Agent': fake_useragent.UserAgent().random
        }
        return proxies, headers

    def xiaoxiang_tunnel(self):
        tunnel = config.xiaoxiang_tunnel
        proxy_username = config.xiaoxiang_username
        proxy_pwd = config.xiaoxiang_password
        proxyMeta = "http://%(user)s:%(pass)s@%(tunnel)s" % {"user": proxy_username, "pass": proxy_pwd, "tunnel": tunnel}
        proxies = {
            'http': proxyMeta,
            'https': proxyMeta,
        }
        headers = {
            'User-Agent': fake_useragent.UserAgent().random
        }
        return proxies, headers

    def mogu_tunnel(self):
        tunnel = config.mogu_tunnel
        appKey = config.mogu_appkey
        proxies = {
            "http": "http://" + tunnel,
            "https": "https://" + tunnel
        }
        headers = {
            "Proxy-Authorization": 'Basic '+ appKey,
            "User-Agent": fake_useragent.UserAgent().random
        }
        return proxies, headers

    def wuyou_tunnel(self):
        tunnel = config.wuyou_tunnel
        username = config.wuyou_username
        password = config.wuyou_password
        proxies = {
            "http": "http://%(user)s:%(pwd)s@%(tunnel)s/" % {"user": username, "pwd": password, "tunnel": tunnel},
            "https": "http://%(user)s:%(pwd)s@%(tunnel)s/" % {"user": username, "pwd": password, "tunnel": tunnel}
        }
        headers = {
            'User-Agent': fake_useragent.UserAgent().random
        }
        return proxies, headers

    def xundaili_tunnel(self):
        orderno = config.xundaili_orderno
        secret = config.xundaili_secret
        ip_port = config.xundaili_tunnel
        timestamp = str(int(time.time()))  # 计算时间戳
        txt = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
        md5_string = hashlib.md5(txt.encode()).hexdigest()  # 计算sign
        sign = md5_string.upper()  # 转换成大写
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp + "&change=true"
        proxies = {
            "http": "http://" + ip_port,
            "https": "htts://" + ip_port
        }
        headers = {
            "Proxy-Authorization": auth,
            "User-Agent": fake_useragent.UserAgent().random
        }
        return proxies, headers


class GetCmd:
    def __init__(self):
        self.supplier_cmd_dict = {
            "abuyun": self.abuyun_cmd(),
            "kuaidaili": self.kuaidaili_cmd(),
            "xiongmao": self.xiongmao_cmd(),
            "xiaoxiang": self.xiaoxiang_cmd(),
            "mogu": self.mogu_cmd(),
            "wuyou": self.wuyou_cmd(),
            "xundaili": self.xundaili_cmd()
        }

    def get_cmd(self, supplier):
        return self.supplier_cmd_dict[supplier]

    def kuaidaili_cmd(self):
        cmd = "curl -o /dev/null  -x %(username)s:%(password)s@%(tunnel)s -m %(timeout)s '%(bandwidth_test_url)s' -k " % {
            "username": config.kuaidaili_username,
            "password": config.kuaidaili_password,
            "tunnel": config.kuaidaili_tunnel,
            "timeout": config.bandwidth_test_timeout,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd

    def xiongmao_cmd(self):
        orderno = config.xiongmao_orderno
        secret = config.xiongmao_secret
        timestamp = str(int(time.time()))  # 计算时间戳
        txt = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
        md5_string = hashlib.md5(txt.encode()).hexdigest()  # 计算sign
        sign = md5_string.upper()  # 转换成大写
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp + "&change=true"
        cmd = "curl -o /dev/null  -x %(tunnel)s -m %(timeout)s -H 'Proxy-Authorization:%(auth)s' '%(bandwidth_test_url)s' -k " % {
            "tunnel": config.xiongmao_tunnel,
            "timeout": config.bandwidth_test_timeout,
            "auth": auth,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd

    def abuyun_cmd(self):
        cmd = "curl -o /dev/null  -x %(username)s:%(password)s@%(tunnel)s -m %(timeout)s '%(bandwidth_test_url)s' -k " % {
            "username": config.abuyun_username,
            "password": config.abuyun_password,
            "tunnel": config.abuyun_tunnel,
            "timeout": config.bandwidth_test_timeout,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd

    def xiaoxiang_cmd(self):
        cmd = "curl -o /dev/null  -x %(username)s:%(password)s@%(tunnel)s -m %(timeout)s '%(bandwidth_test_url)s' -k " % {
            "username": config.xiaoxiang_username,
            "password": config.xiaoxiang_password,
            "tunnel": config.xiaoxiang_tunnel,
            "timeout": config.bandwidth_test_timeout,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd

    def mogu_cmd(self):
        cmd = "curl -o /dev/null  -x %(tunnel)s -m %(timeout)s -H 'Proxy-Authorization:Basic %(appkey)s' '%(bandwidth_test_url)s' -k " % {
            "tunnel": config.mogu_tunnel,
            "appkey": config.mogu_appkey,
            "timeout": config.bandwidth_test_timeout,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd

    def wuyou_cmd(self):
        cmd = "curl -o /dev/null  -x %(username)s:%(password)s@%(tunnel)s -m %(timeout)s '%(bandwidth_test_url)s' -k " % {
            "username": config.wuyou_username,
            "password": config.wuyou_password,
            "tunnel": config.wuyou_tunnel,
            "timeout": config.bandwidth_test_timeout,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd

    def xundaili_cmd(self):
        orderno = config.xundaili_orderno
        secret = config.xundaili_secret
        timestamp = str(int(time.time()))  # 计算时间戳
        txt = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp
        md5_string = hashlib.md5(txt.encode()).hexdigest()  # 计算sign
        sign = md5_string.upper()  # 转换成大写
        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp + "&change=true"
        cmd = "curl -o /dev/null  -x %(tunnel)s -m %(timeout)s -H 'Proxy-Authorization:%(auth)s' '%(bandwidth_test_url)s' -k " % {
            "tunnel": config.xundaili_tunnel,
            "timeout": config.bandwidth_test_timeout,
            "auth": auth,
            "bandwidth_test_url": config.bandwidth_test_url
        }
        cmd = cmd + "-sw %{speed_download}"
        return cmd


# checkutils
class BaseCheck:
    def __init__(self, supplier):
        self.supplier = supplier
        self.proxies, self.headers = GetTunnel().get_tunnel(self.supplier)
        self.check_url = config.base_test_url
        self.re = re.compile(r'IP\t: (.*?)</pre>', re.S)
        self.now = lambda :time.time()
        self.log = get_logger(supplier=supplier, type="Base")
        self.exception_time_list = []

    # 断网检测
    def network_out_check(self):
        if len(self.exception_time_list) < 20:
            self.exception_time_list.append(datetime.now())
        else:
            if datetime.now() - self.exception_time_list[0] < timedelta(
                    seconds=5):
                self.log.error("检测断网!")
                os._exit(0)
            else:
                self.exception_time_list.pop(0)
                self.exception_time_list.append(datetime.now())

    @timeout(config.base_test_timeout)
    def base_test(self, db):
        t1 = self.now()
        try:
            resp = requests.get(self.check_url, headers=self.headers,
                                proxies=self.proxies,
                                timeout=8, verify=False)
            if resp.status_code == 200:
                ip_infos = self.re.findall(resp.text)[0].split('\n')
                proxy_ip = ip_infos[0].strip()
                location = ip_infos[1].split(':')[1].strip()
                location_split = location.split("  ")
                prov, city = "", ""
                if len(location_split) == 3:
                    prov, city = location_split[1], location_split[2]
                elif len(location_split) == 2:
                    city = location_split[1]
                resp_speed = resp.elapsed.total_seconds()
                self.log.info(
                    'proxy_ip:%(proxy_ip)s, prov:%(prov)s, city:%(city)s, resp_speed:%(resp_speed)s' % {
                        "proxy_ip": proxy_ip, "prov": prov, "city": city,
                        "resp_speed": resp_speed})
                self.put_in_localdb(db, supplier=self.supplier,
                               resp_speed=resp_speed,
                               location=location, prov=prov, city=city,
                               proxy_ip=proxy_ip)
            else:
                self.log.debug('-->status_code:%s' % resp.status_code)
                self.put_in_localdb(db, supplier=self.supplier, is_ok=0)
        except Exception as e:
            self.log.error('dotask error-->%s' % str(e))
            self.put_in_localdb(db, supplier=self.supplier, is_ok=0)
            self.network_out_check()
        # 保证每次运行的间隔至少为1s
        run_time = self.now() - t1
        if run_time < 1:
            time.sleep(1 - run_time)

    def put_in_localdb(self, db, supplier='', resp_speed=0,
                       location='', prov='', city='', proxy_ip='',
                       is_ok=1, request_method="GET"):
        insert_sql = "insert into tunnel_info1(supplier, resp_speed, target_url, location, prov, city, proxy_ip, is_ok, request_method) values('%(supplier)s', %(resp_speed)s, '%(target_url)s', '%(location)s', '%(prov)s', '%(city)s', '%(proxy_ip)s', %(is_ok)s, '%(request_method)s')" \
                     % {"supplier": supplier, "resp_speed": resp_speed,
                        "target_url": self.check_url, "location": location,
                        "prov": prov, "city": city,
                        "proxy_ip": proxy_ip, "is_ok": is_ok,
                        "request_method": request_method}
        try:
            db.execute(insert_sql)
        except Exception as e:
            self.log.error('put_in_localdb error-->%s' % e)
            pass

    # 通过cip.cc获取ip、地区分布以及响应时间,并将结果入库
    def run(self):
        db = get_db_local()
        while True:
            try:
                self.base_test(db)
            except TimeoutError as e:
                self.log.error('bandwidth_test Timeout!')
                self.put_in_localdb(db, supplier=self.supplier, is_ok=0)
                self.network_out_check()



class BandwidthCheck:
    def __init__(self, supplier):
        self.supplier = supplier
        self.cmd = GetCmd().get_cmd(self.supplier)
        self.db = get_db_local()
        self.download_url = config.bandwidth_test_url
        self.now = lambda: time.time()
        self.log = get_logger(supplier=supplier, type="Bandwidth")
        self.exception_time_list = []

    # 断网检测
    def network_out_check(self):
        if len(self.exception_time_list) < 10:
            self.exception_time_list.append(datetime.now())
        else:
            if datetime.now() - self.exception_time_list[0] < timedelta(minutes=1):
                self.log.error("检测断网!")
                os._exit(0)
            else:
                self.exception_time_list.pop(0)
                self.exception_time_list.append(datetime.now())

    # 宽带测试
    def bandwidth_test(self):
        try:
            res = subprocess.Popen(self.cmd, shell=True, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            bandwidth = res.communicate()[0].decode()  # 单位:B/s
            bandwidth = float(bandwidth)
            if bandwidth:
                self.put_in_localdb(bandwidth=bandwidth)
                self.log.debug("-->%s" % bandwidth)
            else:
                self.put_in_localdb(is_ok=0)
                self.network_out_check()
        except Exception as e:
            self.log.error('bandwidth error-->%s' % str(e))
            self.put_in_localdb(is_ok=0)
            self.network_out_check()

    def put_in_localdb(self, bandwidth=0, is_ok=1):
        insert_sql = "insert into tunnel_info2(supplier, download_url, bandwidth, is_ok, timeout) values('%(supplier)s', '%(download_url)s', %(bandwidth)s, %(is_ok)s, %(timeout)s)" \
                     % {"supplier": self.supplier,
                        "download_url": self.download_url,
                        "bandwidth": bandwidth, "is_ok": is_ok,
                        "timeout": config.bandwidth_test_timeout}
        try:
            self.db.execute(insert_sql)
        except Exception as e:
            self.log.error('put_in_localdb error-->%s' % e)

    def run(self):
        while True:
            self.bandwidth_test()
            # 测完一轮后休眠2秒
            time.sleep(2)






