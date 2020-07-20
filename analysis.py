# -*- coding: utf-8 -*-
import prettytable as pt
from utils import get_db_local

def get_analysis(db):
    cursor = db.execute("SELECT supplier, count(*) from `tunnel_info1` GROUP BY	supplier;")
    supplierList = [(x[0], x[1]) for x in cursor.fetchall()]
    # print(supplierList)
    speed_ret, ip_ret, bandwidth_ret = [], [], []
    for supplier in supplierList:
        _supplier = supplier[0]
        req_total_count = supplier[1]  # 请求总量

        # 获取成功响应数量
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(supplier[0],))
        resp_ok_count = cursor.fetchone()[0]  # 成功响应数量
        resp_ok_rate = resp_ok_count / req_total_count if req_total_count else 0  # 成功响应率

        # 获取响应时长小于1秒的数量
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<1;".format(supplier[0],))
        resp_lt_1_count = cursor.fetchone()[0]  # 响应时长小于1s的数量
        resp_lt_1_rate =resp_lt_1_count / resp_ok_count if resp_ok_count else 0  # 响应时长小于1s的占比

        # 获取响应时间小于2秒的数量
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<2;".format(supplier[0],))
        resp_lt_2_count = cursor.fetchone()[0]  # 响应时长小于2s的数量
        resp_lt_2_rate = resp_lt_2_count / resp_ok_count if resp_ok_count else 0  # 响应时长小于2s的占比

        # 获取响应时间小于5秒的数量
        cursor = db.execute(
            "SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<5;".format(supplier[0], ))
        resp_lt_5_count = cursor.fetchone()[0]  # 响应时长小于5s的数量
        resp_lt_5_rate = resp_lt_5_count / resp_ok_count if resp_ok_count else 0  # 响应时长小于5s的占比

        # 从小于5秒的响应中获取平均响应速度
        cursor = db.execute("SELECT AVG(resp_speed) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<5;".format(supplier[0],))
        avg_resp_speed = cursor.fetchone()[0]  # 平均响应时长

        # 从小于5秒的响应中获取响应速度方差
        cursor = db.execute("SELECT VARIANCE(resp_speed) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<5;".format(supplier[0],))
        var_resp_speed = cursor.fetchone()[0]  # 响应时长方差


        # 获取IP总量
        cursor = db.execute("SELECT count(DISTINCT proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(supplier[0],))
        ip_total_count = cursor.fetchone()[0]  # ip总量
        ip_repetitive_rate = (resp_ok_count - ip_total_count) / resp_ok_count if resp_ok_count else 0  # ip总重复率

        cursor = db.execute("SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-16 00:00:00' and created_time<'2020-07-16 00:01:00';".format(supplier[0], ))
        tmp = cursor.fetchone()
        ip_1_mi_count, ip_1_mi_total_count = tmp[0], tmp[1]
        ip_repetitive_rate_1_mi = (ip_1_mi_total_count - ip_1_mi_count) / ip_1_mi_total_count if ip_1_mi_total_count else 0  # ip1分钟重复率

        cursor = db.execute("SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-16 00:00:00' and created_time<'2020-07-16 00:05:00';".format(supplier[0], ))
        tmp = cursor.fetchone()
        ip_5_mi_count, ip_5_mi_total_count = tmp[0], tmp[1]
        ip_repetitive_rate_5_mi = (ip_5_mi_total_count - ip_5_mi_count) / ip_5_mi_total_count if ip_5_mi_total_count else 0  # ip5分钟重复率

        cursor = db.execute("SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-16 00:00:00' and created_time<'2020-07-16 01:00:00';".format(supplier[0], ))
        tmp = cursor.fetchone()
        ip_1_h_count, ip_1_h_total_count = tmp[0], tmp[1]
        ip_repetitive_rate_1_h = (ip_1_h_total_count - ip_1_h_count) / ip_1_h_total_count if ip_1_h_total_count else 0  # ip1小时重复率

        cursor = db.execute("SELECT count(DISTINCT proxy_ip),count(proxy_ip) from `tunnel_info1` where supplier='{}' and is_ok=1 and created_time>='2020-07-16 00:00:00' and created_time<'2020-07-17 00:00:00';".format(supplier[0], ))
        tmp = cursor.fetchone()
        ip_1_d_count, ip_1_d_total_count = tmp[0], tmp[1]
        ip_repetitive_rate_1_d = (ip_1_d_total_count - ip_1_d_count) / ip_1_d_total_count if ip_1_d_total_count else 0  # ip1天重复率

        # 获取IP prov分布
        cursor = db.execute("SELECT count(DISTINCT prov) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(supplier[0],))
        ip_prov_count = cursor.fetchone()[0]  # ip省分布数量

        # 获取IP city分布
        cursor = db.execute("SELECT count(DISTINCT city) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(supplier[0],))
        ip_city_count = cursor.fetchone()[0]  # ip市分布数量


        # 各代理商带宽情况
        # 获取带宽请求总量
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}';".format(supplier[0],))
        band_total_count = cursor.fetchone()[0]  # 带宽请求总量

        # 获取带宽有效响应数量
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}' and is_ok=1;".format(supplier[0],))
        band_ok_count = cursor.fetchone()[0]  # 带宽有效响应数量
        band_ok_rate = band_ok_count / band_total_count if band_total_count else 0  # 带宽有效响应率

        # 获取带宽平均值
        cursor = db.execute("SELECT AVG(bandwidth) from `tunnel_info2` where supplier='{}' and is_ok=1;".format(supplier[0],))
        avg_bandwidth = cursor.fetchone()[0]
        avg_bandwidth = avg_bandwidth / 1024 if avg_bandwidth else None   # 有效响应带宽平均值

        # 获取带宽<100K的数量
        threshold_100 = 1024 * 100
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}' and is_ok=1 and bandwidth < {};".format(supplier[0], threshold_100))
        band_lt_100_count = cursor.fetchone()[0]
        band_lt_100_rate = band_lt_100_count / band_ok_count if band_ok_count else 0  # 带宽<100K占比

        # 获取带宽大于100小于300的数量
        threshold_300 = 1024 * 300
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}' and is_ok=1 and bandwidth > {} and bandwidth < {};".format(supplier[0], threshold_100, threshold_300))
        band_100_300_count = cursor.fetchone()[0]
        band_100_300_rate = band_100_300_count / band_ok_count if band_ok_count else 0  # 带宽<100K and >300K占比

        # 获取带宽大于400小于500的数量
        threshold_400 = 1024 * 400
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}' and is_ok=1 and bandwidth > {} and bandwidth < {};".format(supplier[0], threshold_300, threshold_400))
        band_300_400_count = cursor.fetchone()[0]
        band_300_400_rate = band_300_400_count / band_ok_count if band_ok_count else 0  # 带宽<300K and >400K占比

        # 获取带宽大于400小于500的数量
        threshold_500 = 1024 * 500
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}' and is_ok=1 and bandwidth > {} and bandwidth < {};".format(supplier[0], threshold_400, threshold_500))
        band_400_500_count = cursor.fetchone()[0]
        band_400_500_rate = band_400_500_count / band_ok_count if band_ok_count else 0  # 带宽<400K and >500K占比

        # 获取带宽>500K的数量
        cursor = db.execute("SELECT count(*) from `tunnel_info2` where supplier='{}' and is_ok=1 and bandwidth > {};".format(supplier[0], threshold_500))
        band_gt_500_count = cursor.fetchone()[0]
        band_gt_500_rate = band_gt_500_count / band_ok_count if band_ok_count else 0  # 带宽>500K占比


        # 响应数据分析
        speed_tmp = {
            "supplier": _supplier,
            "req_total_count": req_total_count,
            "resp_ok_count": resp_ok_count,
            "resp_ok_rate": "%.3f" % resp_ok_rate,
            "resp_lt_1_rate": "%.2f" % resp_lt_1_rate,
            "resp_lt_2_rate": "%.2f" % resp_lt_2_rate,
            "resp_lt_5_rate": "%.2f" % resp_lt_5_rate,
            "avg_resp_speed": "%.2f" % avg_resp_speed,
            "var_resp_speed": "%.4f" % var_resp_speed,
        }
        speed_ret.append(speed_tmp)

        # ip数据分析
        ip_tmp = {
            "supplier": _supplier,
            "req_total_count": req_total_count,
            "ip_total_count": ip_total_count,
            "ip_repetitive_rate": "%.2f" % ip_repetitive_rate,
            "ip_repetitive_rate_1_mi": "%.2f" % ip_repetitive_rate_1_mi,
            "ip_repetitive_rate_5_mi": "%.2f" % ip_repetitive_rate_5_mi,
            "ip_repetitive_rate_1_h": "%.2f" % ip_repetitive_rate_1_h,
            "ip_repetitive_rate_1_d": "%.2f" % ip_repetitive_rate_1_d,
            "ip_prov_count": ip_prov_count,
            "ip_city_count": ip_city_count
        }
        ip_ret.append(ip_tmp)

        # 带宽数据分析
        bandwidth_tmp = {
            "supplier": _supplier,
            "band_total_count": band_total_count,
            "band_ok_count": band_ok_count,
            "band_ok_rate": "%.3f" % band_ok_rate,
            "avg_bandwidth": "%.2fK" % avg_bandwidth,
            "band_lt_100_rate": "%.3f" % band_lt_100_rate,
            "band_100_300_rate": "%.3f" % band_100_300_rate,
            "band_300_400_rate": "%.3f" % band_300_400_rate,
            "band_400_500_rate": "%.3f" % band_400_500_rate,
            "band_gt_500_rate": "%.3f" % band_gt_500_rate
        }
        bandwidth_ret.append(bandwidth_tmp)

    return (speed_ret, ip_ret, bandwidth_ret)

def trans2table(speed_data, ip_data, bandwidth_data):
    assert len(speed_data)!=0, "speed_data  长度为零！！！"
    assert len(ip_data)!=0, "ip_data  长度为零！！！"
    assert len(bandwidth_data)!=0, "bandwidth_data  长度为零！！！"
    speed_tb = pt.PrettyTable()
    ip_tb = pt.PrettyTable()
    bandwidth_tb = pt.PrettyTable()
    speed_tb.field_names = [
        "supplier",
        "req_total_count",
        "resp_ok_count",
        "resp_ok_rate",
        "resp_lt_1_rate",
        "resp_lt_2_rate",
        "resp_lt_5_rate",
        "avg_resp_speed",
        "var_resp_speed",
    ]
    ip_tb.field_names = [
        "supplier", "req_total_count",
        "ip_total_count", "ip_repetitive_rate",
        "ip_repetitive_rate_1_mi",
        "ip_repetitive_rate_5_mi",
        "ip_repetitive_rate_1_h",
        "ip_repetitive_rate_1_d",
        "ip_prov_count",
        "ip_city_count"
    ]
    bandwidth_tb.field_names = [
        "supplier",
        "band_total_count",
        "band_ok_count",
        "band_ok_rate",
        "avg_bandwidth",
        "band_lt_100_rate",
        "band_100_300_rate",
        "band_300_400_rate",
        "band_400_500_rate",
        "band_gt_500_rate"
    ]

    for r in speed_data:
        speed_tb.add_row([r[x] for x in speed_tb.field_names])
    print(speed_tb)
    for r in ip_data:
        ip_tb.add_row([r[x] for x in ip_tb.field_names])
    print(ip_tb)
    for r in bandwidth_data:
        bandwidth_tb.add_row([r[x] for x in bandwidth_tb.field_names])
    print(bandwidth_tb)

def main():
    db = get_db_local()
    speed_data, ip_data, bandwidth_data = get_analysis(db)
    trans2table(speed_data, ip_data, bandwidth_data)

if __name__ == "__main__":
    main()
