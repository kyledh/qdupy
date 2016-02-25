# -*- coding: utf-8 -*-

from PIL import Image
import io
import re
import requests
import pytesseract
from lxml import etree

# 教务登录


def login(sid, pwd):
    l = requests.Session()
    loginurl = 'http://jw.qdu.edu.cn/academic/j_acegi_security_check'
    codeurl = 'http://jw.qdu.edu.cn/academic/getCaptcha.do'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
    }

    # 验证码
    code = l.get(codeurl, headers=headers, stream=True)

    # 登录
    postdata = {
        'j_username': sid,
        'j_password': pwd,
        'j_captcha': codetext(code.content)
    }
    r = l.post(loginurl, postdata)

    # 密码错误
    if re.search(u'\u5bc6\u7801\u4e0d\u5339\u914d', r.text):
        return 400

    # 用户名不存在
    elif re.search(u'\u4e0d\u5b58\u5728', r.text):
        return 404

    # 验证码错误
    elif re.search(u'\u9a8c\u8bc1\u7801\u4e0d\u6b63\u786e', r.text):
        return login(sid, pwd)

    # 成功
    else:
        # userid = re.findall(b'.*?userid=(.*?)"', userpage, re.S)
        # for i in userid:
        #     uid = userid * 10 + int(i)
        return l.cookies

# 查询成绩


def scores(cookies, year, term):
    scoresurl = 'http://jw.qdu.edu.cn/academic/manager/score/studentOwnScore.do'

    # 字符串计算  eval()
    postdata = {
        'year': eval(year + '-' + '1980'),
        'term': term,
        'para': '0'
    }

    scorespage = requests.post(scoresurl, postdata, cookies=cookies).content
    aa = '<td>' + year + \
        '[\s\S]*?<td>[\s\S]*?<td>(.*?)[\s].*?</td>[\s\S]*?</td>[\s\S]*?<td>(.*?)[\s].*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>[\s\S]*?</td>'

    # str转types  .encode(encoding="utf-8")
    scores = re.findall(aa.encode(encoding="utf-8"), scorespage, re.S)
    # for s in scores:
    #     print
    #     print s[0] + ' : ' + s[1]

    # data = []
    tmp = {}
    for s in scores:
        tmp[s[0]] = s[1]
    return tmp

# 验证码识别


def codetext(code):
    img = Image.open(io.BytesIO(code))

    # 降噪
    threshold = 140
    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)

    # 将彩色图像转换为灰度图像
    imgry = img.convert('L')

    # 讲图像中噪声去除
    out = imgry.point(table, '1')

    codetext = pytesseract.image_to_string(out, config='digits')

    # 去除空格，将.替换为0
    codetext = codetext.replace(' ', '').replace('.', '0')

    return codetext

# 查询课表


def kebiao(s, uid):
    year = raw_input('请输入查询学年: ')
    term = raw_input('春季学期输入[1],秋季学期输入[2]: ')
    print
    get = {
        'id': uid,
        'yearid': eval(year + '-' + '1980'),
        'termid': term,
        'timetableType': 'STUDENT',
        'sectionType': 'COMBINE'
    }

    kb = s.get(
        'http://jw.qdu.edu.cn/academic/manager/coursearrange/showTimetable.do', params=get)
    html = etree.HTML(kb.content)

    kb = html.xpath('//*[@id="timetable"]//*[@class="center"]')
    i = 0
    for k in kb:
        # print k.xpath('string()').encode('utf-8')
        if i < 7:
            list.append(
                k.text.split(';')[0].replace('<<', '').replace('>>', ''))
            i += 1

# 教务通知


def news():
    newsurl = requests.get(
        'http://jw.qdu.edu.cn/homepage/infoArticleList.do;jsessionid=E06A6E2B5FA3F797FAB8FA5F6331AC92?columnId=358')
    html = etree.HTML(newsurl.content.decode('utf-8', 'ignore'))
    news = html.xpath('//*[@id="thirdcontent"]/div[2]/ul/li/div/a')
    for new in news:
        print new.xpath('string(.)').encode('utf-8').replace(' ', '').replace('\n', '')
        print 'http://jw.qdu.edu.cn/homepage/' + new.attrib['href']
        print

# 个人信息


def userinfo(cookies):
    user = requests.get(
        'http://jw.qdu.edu.cn/academic/showPersonalInfo.do', cookies=cookies)
    html = etree.HTML(user.content.decode('utf-8', 'ignore'))
    # 姓名
    for n in html.xpath('/html/body/center/table[1]/tr[1]/td[2]/text()'):
        xm = n.encode('utf-8').decode("utf-8")
    # 院系
    for n in html.xpath('/html/body/center/table[1]/tr[2]/td[1]/text()'):
        yx = n.encode('utf-8').decode("utf-8")
    # 专业
    for n in html.xpath('/html/body/center/table[1]/tr[2]/td[2]/text()'):
        zy = n.encode('utf-8').decode("utf-8")
    # 班级
    for n in html.xpath('/html/body/center/table[1]/tr[4]/td[2]/text()'):
        bj = n.encode('utf-8').decode("utf-8")
    # for n in html.xpath('/html/body/center/table[1]/tr[4]/td[1]/text()'):
    #     print '年级: ' + n.encode('utf-8')

    data = {
        'xm': xm,
        'yx': yx,
        'zy': zy,
        'bj': bj,
    }
    # data = {
    #     '姓名：' : xm,
    #     '院系：' : yx,
    #     '专业：' : zy,
    #     '班级：' : bj,
    # }

    # jsonn = json.dumps(data)

    # print jsonn

    return data
