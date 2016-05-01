# -*- coding: utf-8 -*-

from PIL import Image
import io
import re
import requests
import pytesseract
from lxml import etree


# 教务登录
def login(sid, pwd):
    r = requests.Session()
    loginurl = 'http://jw.qdu.edu.cn/academic/j_acegi_security_check'
    codeurl = 'http://jw.qdu.edu.cn/academic/getCaptcha.do'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36'
    }

    # 验证码
    code = r.get(codeurl, headers=headers, stream=True)

    # 登录
    postdata = {
        'j_username': sid,
        'j_password': pwd,
        'j_captcha': codetext(code.content)
    }
    res = r.post(loginurl, postdata)

    # 成功
    if re.search(u'\u7efc\u5408\u6559\u52a1\u7ba1\u7406\u7cfb\u7edf', res.text):
        return r.cookies

    # 验证码错误
    elif re.search(u'\u9a8c\u8bc1\u7801\u4e0d\u6b63\u786e', res.text):
        return login(sid, pwd)

    else:
        return False


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

    _scores = {}
    for s in scores:
        _scores[s[0]] = s[1]
    return _scores


# 教务通知
def news():
    newsurl = requests.get(
        'http://jw.qdu.edu.cn/homepage/infoArticleList.do;jsessionid=E06A6E2B5FA3F797FAB8FA5F6331AC92?columnId=358')
    html = etree.HTML(newsurl.content.decode('utf-8', 'ignore'))
    news = html.xpath('//*[@id="thirdcontent"]/div[2]/ul/li/div/a')

    _news = {}
    for new in news:
        _new = {}
        _new['title'] = _replace(new.xpath('string(.)').encode('utf-8'))
        _new['url'] = 'http://jw.qdu.edu.cn/homepage/' + new.attrib['href']
        id = re.findall(r'(\d{4})', new.attrib['href'])
        _news[id] = _new

    return _news


# 个人信息
def userinfo(cookies):
    user = requests.get(
        'http://jw.qdu.edu.cn/academic/showPersonalInfo.do', cookies=cookies)
    html = etree.HTML(user.content.decode('utf-8', 'ignore'))

    _userinfo = {}

    # 姓名 院系 专业 班级
    _userinfo[u'姓名'] = _replace(html.xpath('/html/body/center/table[1]/tr[1]/td[2]/text()')[0])
    _userinfo[u'院系'] = _replace(html.xpath('/html/body/center/table[1]/tr[2]/td[1]/text()')[0])
    _userinfo[u'专业'] = _replace(html.xpath('/html/body/center/table[1]/tr[2]/td[2]/text()')[0])
    _userinfo[u'班级'] = _replace(html.xpath('/html/body/center/table[1]/tr[4]/td[2]/text()')[0])

    return _userinfo


# 四六级
def cet(zkzh, xm):
    header = {
        'Host': 'www.chsi.com.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
        'Referer': 'http://www.chsi.com.cn/cet/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    data = {'zkzh': zkzh, 'xm': xm}
    res = requests.get('http://www.chsi.com.cn/cet/query', params=data, headers=header).content
    html = etree.HTML(res.decode('utf-8', 'ignore'))

    if not re.search(zkzh, res):
        return False

    _cetinfo = {}

    # 学校 考试类别 考试时间 总分 听力 阅读 写作与翻译
    _cetinfo[u'学校'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[2]/td/text()')[0])
    _cetinfo[u'考试类别'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[3]/td/text()')[0])
    _cetinfo[u'考试时间'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[5]/td/text()')[0])
    _cetinfo[u'总分'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[6]/td/span[1]/text()')[0])
    _cetinfo[u'听力'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[6]/td/text()')[2])
    _cetinfo[u'阅读'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[6]/td/text()')[3])
    _cetinfo[u'写作与翻译'] = _replace(html.xpath('//*[@id="leftH"]/div/table/tr[6]/td/text()')[4])

    return _cetinfo


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


# 去除多余内容
def _replace(str):
    return str.replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')