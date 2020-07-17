# -*- coding: utf-8 -*-
import prettytable as pt
from utils import get_db_local

def get_analysis(db):
    cursor = db.execute("SELECT supplier, count(*) from `tunnel_info1` GROUP BY	supplier;")
    supplierList = [(x[0], x[1]) for x in cursor.fetchall()]
    # print(supplierList)
    ret = []
    for supplier in supplierList:
        # print(supplier)
        total_count = supplier[1]

        # 获取有效请求数
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        ip_ok_count = cursor.fetchone()[0]
        ip_ok_rate = ip_ok_count / total_count

        # 获取优质响应数 响应时间小于1秒的
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<1;".format(
            supplier[0],
        ))
        resp_lt_1_count = cursor.fetchone()[0]
        resp_lt_1_rate =resp_lt_1_count / ip_ok_count

        # 获取响应时间小于2秒的响应
        cursor = db.execute(
            "SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<1;".format(
                supplier[0],
            ))
        resp_lt_2_count = cursor.fetchone()[0]
        resp_lt_2_rate = resp_lt_2_count / ip_ok_count


        # 从小于2秒的响应中获取平均响应速度
        cursor = db.execute(
            "SELECT AVG(resp_speed) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<2;".format(
                supplier[0],
            ))
        avg_resp_speed = cursor.fetchone()[0]

        # 从小于2秒的响应中获取响应速度方差
        cursor = db.execute("SELECT VARIANCE(resp_speed) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        var_resp_speed = cursor.fetchone()[0]

        # 获取IP city分布
        cursor = db.execute(
            "SELECT count(DISTINCT prov) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
                supplier[0],
            ))
        ip_prov_count = cursor.fetchone()[0]

        # 获取IP city分布
        cursor = db.execute("SELECT count(DISTINCT city) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        ip_city_count = cursor.fetchone()[0]

        # 获取IP总量
        cursor = db.execute("SELECT count(DISTINCT proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        ip_total_count = cursor.fetchone()[0]
        # ip重复率
        ip_repetitive_rate = ip_total_count / ip_ok_count

        cursor = db.execute(
            "SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-17 00:00:00' and created_time<'2020-07-17 00:01:00';".format(
                supplier[0],
            ))
        tmp =  cursor.fetchone()
        ip_1_mi_count, ip_1_mi_total_count = tmp[0], tmp[1]
        # ip1分钟重复率
        ip_repetitive_rate_1_mi = ip_1_mi_count / ip_1_mi_total_count

        cursor = db.execute(
            "SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-17 00:00:00' and created_time<'2020-07-17 00:05:00';".format(
                supplier[0],
            ))
        tmp = cursor.fetchone()
        ip_5_mi_count, ip_5_mi_total_count = tmp[0], tmp[1]
        # ip5分钟重复率
        ip_repetitive_rate_5_mi = ip_5_mi_count / ip_5_mi_total_count

        cursor = db.execute(
            "SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-17 00:00:00' and created_time<'2020-07-17 01:00:00';".format(
                supplier[0],
            ))
        tmp = cursor.fetchone()
        ip_1_h_count, ip_1_h_total_count = tmp[0], tmp[1]
        # ip1小时重复率
        ip_repetitive_rate_1_h = ip_1_h_count / ip_1_h_total_count

        cursor = db.execute(
            "SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-15 00:00:00' and created_time<'2020-07-16 00:00:00';".format(
                supplier[0],
            ))
        tmp = cursor.fetchone()
        ip_1_d_count, ip_1_d_total_count = tmp[0], tmp[1]
        # ip1小时重复率
        ip_repetitive_rate_1_d = ip_1_d_count / ip_1_d_total_count

        # 求各代理商带宽情况
        ## 获取带宽平均值
        cursor = db.execute(
            "SELECT AVG(bandwidth) from `tunnel_info2` where supplier='{}' and is_ok=1;".format(
                supplier[0],
            ))
        avg_bandwidth = cursor.fetchone()[0]
        avg_bandwidth = avg_bandwidth / 1024 if avg_bandwidth else None

        cursor = db.execute(
            "SELECT count(*) from `tunnel_info2` where supplier='{}';".format(
                supplier[0],
            ))
        band_total_count = cursor.fetchone()[0]

        cursor = db.execute(
            "SELECT count(*) from `tunnel_info2` where supplier='{}and is_ok=1';".format(
                supplier[0],
            ))
        band_ok_count = cursor.fetchone()[0]

        band_ok_rate = band_ok_count / band_total_count

        tmp = {
            "supplier": supplier[0],                            # 供应商
            "total_count": total_count,                         # 请求总量
            "ip_ok_rate": ip_ok_rate,                           # 响应成功率
            "avg_band_width": "%.2fk" % (avg_bandwidth),        # 带宽
            "band_ok_rate": "%.2f " % band_ok_rate,             # 带宽响应成功率
            "resp_lt_1_rate": resp_lt_1_rate,                   # 响应时长小于1秒占比
            "resp_lt_2_rate": resp_lt_2_rate,                   # 响应时长小于2秒占比
            "avg_resp_speed": "%.2fs"%(avg_resp_speed),         # 平均响应时长
            "var_resp_speed": var_resp_speed,                   # 响应时长方差
            "ip_total_count": ip_total_count,                   # ip总量
            "ip_repetitive_rate": ip_repetitive_rate,           # ip重复率
            "ip_repetitive_rate_1_mi": ip_repetitive_rate_1_mi,           # ip重复率
            "ip_repetitive_rate_5_mi": ip_repetitive_rate_5_mi,           # ip重复率
            "ip_repetitive_rate_1_h": ip_repetitive_rate_1_h,           # ip重复率
            "ip_repetitive_rate_1_d": ip_repetitive_rate_1_d,           # ip重复率
            "ip_prov_count": ip_prov_count,                     # ip涉及的省数量
            "ip_city_count": ip_city_count,                     # ip涉及的市数量
        }

        # print(tmp)
        ret.append(tmp)
    return ret

def trans2table(data):
    assert len(data)!=0, "data  长度为零！！！"
    tb = pt.PrettyTable()
    tb.field_names = [c for c in data[0]]
    for c in data:
        tb.add_row([x for x in c.values()])
    print(tb)


if __name__ == "__main__":
    db = get_db_local()
    data = get_analysis(db)
    trans2table(data)
