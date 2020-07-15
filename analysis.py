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

        # 获取有效IP数
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        is_ok_count = cursor.fetchone()[0]

        # 获取有效IP平均响应速度
        cursor = db.execute("SELECT AVG(resp_speed) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        avg_resp_speed = cursor.fetchone()[0]

        # 获取优质响应数 响应时间小于1秒的
        cursor = db.execute("SELECT count(*) from `tunnel_info1` where supplier='{}' and is_ok=1 and resp_speed<1;".format(
            supplier[0],
        ))
        good_resp_count = cursor.fetchone()[0]

        # 获取响应速度方差
        cursor = db.execute("SELECT VARIANCE(resp_speed) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        var_resp_speed = cursor.fetchone()[0]

        # 获取IP city分布
        cursor = db.execute("SELECT count(DISTINCT city) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        ip_dist_count = cursor.fetchone()[0]

        # 获取IP 重复率
        cursor = db.execute("SELECT count(DISTINCT proxy_ip), count(*) from `tunnel_info1` where supplier='{}' and is_ok=1;".format(
            supplier[0],
        ))
        tmp = cursor.fetchone()
        # ip_dist_rate = cursor.fetchone()[0]/cursor.fetchone()[1]
        ip_dist_rate = (tmp[1]-tmp[0])/tmp[1]

        # 求各代理商带宽情况
        ## 获取带宽平均值
        cursor = db.execute(
            "SELECT AVG(bandwidth) from `tunnel_info2` where supplier='{}' and is_ok=1;".format(
                supplier[0],
            ))
        avg_band_width = cursor.fetchone()[0]

        ## 获取带宽方差
        # cursor = db.execute("SELECT VARIANCE(bandwidth) from `tunnel_info2` where supplier='{}' and is_ok=1;".format(
        #     supplier[0],
        # ))
        # var_band_width = cursor.fetchone()[0]

        tmp = {
            "name": supplier[0],
            "total_count": total_count,
            "is_ok_count": is_ok_count,
            "avg_resp_speed": "%.2fs"%(avg_resp_speed),
            "good_resp_count": good_resp_count,
            "var_resp_speed": var_resp_speed,
            "ip_dist_count": ip_dist_count,
            "ip_dist_rate": ip_dist_rate,
            "avg_band_width": "%.2fk" % (
                        avg_band_width / 1024) if avg_band_width else None,
            # "var_band_width": var_band_width/(1024**2) if var_band_width else None,

        }
        # print(tmp)
        ret.append(tmp)



        # print(supplier[0], total_count, is_ok_count, avg_resp_speed, good_resp_count, var_resp_speed, ip_dist_count, ip_dist_rate)
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
