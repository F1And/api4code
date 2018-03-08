公司新来两个妹子一直吐槽这个接口测试用例用excel维护起来十分费脑费事，而且比较low（内心十分赞同但是不能推翻自己),妹子说excel本来就很麻烦的工具，于是偷偷的进行了二次改版。

变更内容如下：

* 1.代码结构

![image.png](http://upload-images.jianshu.io/upload_images/2955280-4b7c7c7ab5a756ce.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/440)

* 2.新增测试报告网页版和版本管理
* 3.新增用例代码化


一、封装一个获取用例的模块

![image.png](http://upload-images.jianshu.io/upload_images/2955280-f7b9015622bf7e57.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1200)

> 用例的写法可以按照yml文件的写法，后缀的文件都可为.conf、.config、.ini。[]中的是测试用例场景，下面的参数内容对应接口用例参数。
>
> 简单介绍下python内置模块ConfigParser：
>    - ConfigParser 是用来读取配置文件的包。配置文件的格式如下：中括号“[ ]”内包含的为section。section 下面为类似于key:value 的配置内容。(key = value也可以具体方法这次不详细展开，之后写一遍关于ConfigParser的用法，懂原理会让工作更轻松。)
>
>  - 这里讲讲为什么配置写在最外层，如果写到文件夹中，怎么都无法读取配置。python执行run命令的时候需要.ini文件跟run 文件在同个文件夹下。所以应该是路径问题导致，之后尝试修复这个BUG。 

（通过操作绝对路径的方法修复此BUG上图已经修复）


这次变更代码实现如下：
```python 
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 基础包：配置服务

import ConfigParser

config = ConfigParser.ConfigParser()


def get_config(filename):
    """
    获取文件配置
    :param filename: 配置文件名
    :return: None
    """
    global config
    try:
        config.read(filename)
        return True
    except Exception, e:
        print ("读取配置失败 %s" % e)


def get_data(title, key):
    """
    参数配置
    :param title: 配置文件的头信息
    :param key: 配置文件的key值
    :return: 配置文件的value
    """
    try:
        value = config.get(title, key)
        return value
    except Exception, e:
        print ("获取参数失败 %s" % e)


def get_title_list():
    """
    获取所有title
    :return: title list
    """
    try:
        title = config.sections()
        return str(title).decode("string_escape")
    except Exception, e:
        print ("获取title信息失败 %s", e)
```


二、封装一个日志的模块

> 这次日志进行了一次更改：会将测试用例返回结果文件内容写入，文件通过mkdocs生成测试报告。
>
> 公司用的微服务，所以对docker有一定涉猎。官方提供了mkdocs的镜像。拉取官网镜像，将数据卷挂载到搭载测试报告的宿主机上，就可以访问了。你只要维护代码的测试用例，自动更新测试报告。
看下展示效果：

![image.png](http://upload-images.jianshu.io/upload_images/2955280-56d2b3383a2521b6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)


代码如下：
```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 基础包：日志服务

import logging
import constants as cs
import logging.handlers


def get_logger(name='report'):
    FORMAT = '%(message)s'
    filename = cs.REPORT_PATH + name + cs.NOW
    logging.basicConfig(level=logging.WARNING, format=FORMAT,
                       filename=filename, filemode='w')
    return logging
```


三、调用接口的requests
代码如下：
```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 基础包：接口测试的封装

import requests
import json


def change_type(value):
    """
    对dict类型进行中文识别
    :param value: 传的数据值
    :return: 转码后的值
    """
    result = eval(json.dumps(value, ensure_ascii=False, encoding="UTF-8"))
    return result


def api(method, url, data, headers):
    """
    定义一个请求接口的方法和需要的参数
    :param method: 请求类型
    :param url: 请求地址
    :param data: 请求参数
    :param headers: 请求headers
    :return: code码
    """
    global results
    try:
        if method == ("post" or "POST"):
            results = requests.post(url, data, headers=headers)
        if method == ("get" or "GET"):
            results = requests.get(url, data, headers=headers)
        response = results.json()
        code = response.get("code")
        return code
    except Exception, e:
        print ("请求失败 %s" % e)
```

####四、业务包调用封装包(common.py)
```python
#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 业务包：通用函数


import lib.tezMysql as mysql
import lib.tezLog as log
import lib.tezRequest as request
import lib.tezConfig as conf
import constants as cs
import os

def prepare_data(host, user, password, db, sql):
    """
    数据准备，添加测试数据
    :param host: 服务地址
    :param user: 用户
    :param password: 密码
    :param db: 数据库名
    :param sql: 执行的SQL
    :return: 
    """
    mysql.connect(host, user, password, db)
    res = mysql.execute(sql)
    mysql.close()
    print ("Run sql: the row number affected is %s" % res)
    return res


def get_prepare_sql(filename, key):
    """
    获取预备执行的SQL
    :param title: 配置文件头信息
    :param key: 配置文件值
    :return: Value 
    """
    try:
        conf.get_config(filename)
        value = conf.get_data(title=cs.TITLE, key=key)
        return value
    except Exception, e:
        print ("获取用例参数值失败 %s" % e)


def reset_report(filename):
    try:
        result = os.path.exists(cs.REPORT_PATH)
        if result == True:
            conf.get_config(filename)
            reportName = eval(conf.get_data(title=cs.REPORT_NAME, key=cs.REPORT))
            report_name = eval(conf.get_data(title=cs.REPORT_NAME, key=cs.R_NAME))
            file = open(cs.YML_REPORT, 'r')
            list_con = file.readlines()
            content = str(list_con).decode("string_escape")
            fileContent = "- [%s, %s]"
            row = "\n"
            con = row + fileContent % (reportName + cs.NOW, report_name)

            if fileContent % (reportName + cs.NOW, report_name) not in content:
                f = open(cs.YML_REPORT, 'a+')
                f.write(con)
            else:
                print ("内容已经存在 %s" % con)
    except Exception, e:
        print ("文件路径不存在 %s", e)


def run_test(filename):
    conf.get_config(filename)
    list = eval(conf.get_title_list())
    reportName = eval(conf.get_data(cs.REPORT_NAME, key=cs.REPORT))
    logging = log.get_logger(reportName)
    for i in range(2, len(list)):
        title = list[i]
        number = eval(conf.get_data(title, key=cs.NUMBER))
        name = str(conf.get_data(title, key=cs.NAME))
        method = str(conf.get_data(title, key=cs.METHOD))
        url = str(conf.get_data(title, key=cs.URL))
        data = request.change_type(conf.get_data(title, key=cs.DATA))
        headers = eval(conf.get_data(title, key=cs.HEADERS))
        testUrl = cs.TEST_URL + url
        actualCode = request.api(method, testUrl, data, headers)
        expectCode = conf.get_data(title, key=cs.CODE)


        if actualCode != expectCode:
            print "FailInfo"
            print number
            logging.warning("- <font color=#FFB5C5 size=3>FailCase : %s", name)
            logging.warning("    - <font color=#FFB5C5 size=3>Number : %s", number)
            logging.warning("    - <font color=#FFB5C5 size=3>Method : %s", method)
            logging.warning("    - <font color=#FFB5C5 size=3>Url : %s", testUrl)
            logging.warning("    - Data : </br> ``` %s ```", data)
            logging.warning("    - Headers : </br> ``` %s ```", headers)
            logging.warning("    - <font color=#FFB5C5 size=3>期望值 : %s", expectCode)
            logging.warning("    - <font color=#FFB5C5 size=3>实际值 : %s", str(actualCode))
            logging.warning("*****************")
        else:
            print number
            print "TrueInfo"
            logging.warning("- <font color=#3cc8b4 size=3> TrueCase %s", name)
            logging.warning("*****************")

```
五、执行包(run.py)
```python
import util.common as common
import sys

# FILENAME = sys.argv[1]

FILENAME = "proUser.ini"

"""1.新建测试报告目录"""
common.reset_report(filename=FILENAME)

"""2.执行测试用例"""
common.run_test(filename=FILENAME)

```
> PS:有个全局变量包constant.py，里面看到是参数目录文件相关的。
