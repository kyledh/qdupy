# -*- coding: utf-8 -*-
from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.validators import Required, NumberRange
from jw import login, userinfo, scores

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
data = []
score = []


class UserForm(Form):
    sid = IntegerField('学号'.decode("utf-8"), validators=[Required()])
    pwd = PasswordField('密码'.decode("utf-8"), validators=[Required()])
    submit = SubmitField('登录'.decode("utf-8"))


class ScoresForm(Form):
    year = IntegerField(
        '学年'.decode("utf-8"), validators=[Required(), NumberRange(min=1996, max=2016)])
    term = IntegerField(
        '学期'.decode("utf-8"), validators=[Required(), NumberRange(min=1, max=2)])
    submit = SubmitField('查询'.decode("utf-8"))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    global cookies, data
    form = UserForm()
    if form.validate_on_submit():
        cookies = login(form.sid.data, form.pwd.data)
        if cookies == 400:
            flash('密码错误！'.decode("utf-8"))
        elif cookies == 404:
            flash('学号错误！'.decode("utf-8"))
        else:
            data = userinfo(cookies)
            session['sid'] = form.sid.data
            return redirect(url_for('user'))
        return render_template('index.html', form=form)
    return render_template('index.html', form=form)


@app.route('/user', methods=['GET', 'POST'])
def user():
    global cookies, data, score
    form = ScoresForm()
    if form.validate_on_submit():
        score = scores(cookies, str(form.year.data), str(form.term.data))
        return redirect(url_for('score'))
    return render_template('index.html', form=form, data=data)


@app.route('/scores', methods=['GET'])
def score():
    global cookies, data, score
    return render_template('index.html', data=data, scores=score)


if __name__ == '__main__':
    manager.run()
