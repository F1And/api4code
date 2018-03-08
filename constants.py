#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 脚本功能：全部变量

import sys
import time
reload(sys)
sys.setdefaultencoding('utf8')

TEST_URL = 'http://127.0.0.1:8080'

REPORT_NAME = '测试报告'
TITLE = '所有数据准备SQL'

METHOD = 'method'
URL = 'url'
DATA = 'data'
NAME = 'name'
NUMBER = 'number'
CODE = 'code'
HEADERS = 'headers'
REPORT = 'report'
R_NAME = 'reportName'

REPORT_PATH = "../api4code/report/docs/"
YML_REPORT = "../api4code/report/mkdocs.yml"


CASE_PATH = "../api4code/case/"

#测试报告内容
API_TEST_FAIL = """
```
 %s Case Fail
 Number: %s
 Method: %s
 Url: %s
 Headers:
 %s
 Data : 
 %s
 期望值 : %s
 实际值 : %s
```
"""

API_TEST_SUCCESS = """
```
 %s Case Pass
 Number: %s
 Method: %s
 Url: %s
 Headers:
 %s
 Data : 
 %s
 期望值 : %s
 实际值 : %s
```
"""

#报告结果统计
RESULT_CONTENT = """
测试结果如下：
<table border="3" width="500px">
  <tr>
    <th style="color: #787878">All</th>
    <th style="color: #3cc8b4">Pass</th>
    <th style="color: #FFB5C5">Fail</th>
  </tr>
  <tr>
    <th style="color: #787878">%s</th>
    <th style="color: #3cc8b4">%s</th>
    <th style="color: #FFB5C5">%s</th>
  </tr>
</table>
"""

NOW = '_' + time.strftime('%Y%m%d', time.localtime(time.time())) + '.md'
PROJECT_TIME = time.strftime('%Y%m%d', time.localtime(time.time()))