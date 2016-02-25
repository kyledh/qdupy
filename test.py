# -*- coding: utf-8 -*-
from jw import login, userinfo, scores
import types

sid = '201440703676'
pwd = 'lily!1007'

cookies = login(sid, pwd)
# print userinfo(cookies)
# print type(userinfo(cookies))

# print '姓名：'
# print type('姓名：'.decode("utf-8"))
# print '姓名：'.decode("utf-8")

data = scores(cookies)

# print type(data)
# print data[1]
# data = json.loads(jsonn)
for d in data.items():
    s = "".join(d).decode("utf-8")
    print s
    print type(s)
