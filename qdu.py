# -*- coding: utf-8 -*-
from flask import Flask
from utils import login, userinfo, scores, news, cet
from flask.ext.restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()


def _login():
    parser.add_argument('sid', type=str, required=True, help=u"学号不能为空")
    parser.add_argument('pwd', type=str, required=True, help=u"密码不能为空")
    args = parser.parse_args()
    cookies = login(args['sid'], args['pwd'])
    if cookies:
        return cookies
    return u"登录失败", 404


class News(Resource):
    def get(self):
        _news = news()
        return _news


class UserInfo(Resource):
    def get(self):
        return ''

    def post(self):
        cookies = _login()
        _userinfo = userinfo(cookies)
        return _userinfo


class Scores(Resource):
    def get(self):
        return ''

    def post(self):
        parser_copy = parser.copy()
        parser_copy.add_argument('year', type=str, required=True, help=u"学年不能为空")
        parser_copy.add_argument('term', type=str, required=True, help=u"学期不能为空")
        args = parser_copy.parse_args()
        cookies = _login()
        _scores = scores(cookies, args['year'], args['term'])
        return _scores


class Cet(Resource):
    def get(self):
        return ''

    def post(self):
        parser.add_argument('zkzh', type=str, required=True, help=u"准考证号不能为空")
        parser.add_argument('xm', type=unicode, required=True, help=u"姓名不能为空")
        args = parser.parse_args()
        _cetinfo = cet(args['zkzh'], args['xm'])
        if _cetinfo:
            return _cetinfo
        return u"姓名或准考证号有误", 404


api.add_resource(UserInfo, '/userinfo')
api.add_resource(Scores, '/scores')
api.add_resource(News, '/news')
api.add_resource(Cet, '/cet')


if __name__ == '__main__':
    app.run(debug=True)
