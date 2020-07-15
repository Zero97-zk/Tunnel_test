# Tunnel_test

#### 测试对象：各个商家的隧道代理（动态转发代理）

#### 测试环境
* **MySQL数据库**
* **python-python3.6**
    * pymysql
    * gevent
    * requests
    * fake-useragent
    * logging
    * prettytable

#### 测试商家
* **阿布云**
* **无忧**
* **快代理**
* **熊猫**
* **小象**
* **蘑菇**
* **讯代理**

#### 测试方向
* **响应速度**
* **带宽**
* **IP量**
* **IP重复率**
* **IP地区分布**
* **可用率**

#### 测试规格
* 5并发-100万数据（除讯代理外）
* 按量-50万数据 （讯代理）-->:由于讯代理没有按并发动态转发且按量相对较贵所以暂且测试50万

#### 脚本介绍
##### 1.测试脚本文件夹-test
* 基础测试：（响应速度，IP，地区）
    * ~~~ python
        base_check = True  # 默认
        ~~~
    * 例：python3 kuaidaili_test.py
* 带宽测试：（带宽）
    * ~~~ python
        base_check = False
        ~~~
    * 例: python3 kuaidaili_test.py
##### 2.日志查看文件夹-log
* 例： tail -f kuaidaili_test.py
##### 3.数据库分析脚本-analysis.py
* 例:  python3 analysis.py
##### 4.配置文件-config.py
##### 5.建表sql语句-sql.txt


