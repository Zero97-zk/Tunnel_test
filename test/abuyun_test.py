# -*- coding: utf-8 -*-
import gevent
import gevent.monkey
gevent.monkey.patch_all()
import sys
sys.path.insert(0, "../")

import utils
import log

Supplier = "abuyun"
base_check = True  # 测试代理ip，响应速度，地区分布等信息时开启，测试带宽信息时关闭

def main():
    print('商家-->%s' % Supplier)
    if base_check:
        check = utils.BaseCheck(supplier=Supplier)
        gevent.joinall([gevent.spawn(check.run) for i in range(5)])
    else:
        check = utils.BandwidthCheck(supplier=Supplier)
        check.run()


if __name__ == '__main__':
    main()
