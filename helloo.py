from flask import Flask, render_template, session, redirect, url_for, flash
from flask.ext.script import Manager
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Required
from jw import login, userinfo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)


class NameForm(Form):
    sid = StringField('Username', validators=[Required()])
    pwd = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Submit')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        # cookies = login(form.sid.data, form.pwd.data)
        old_name=session.get('name')
        if old_name is not None and old_name != form.sid.data:
            flash('Looks like you have changed your name!')
        session['name'] = form.sid.data
        # uname = user(cookies)
        # print uname
        return redirect(url_for('index'))
    return render_template('index.html', form=form, name=session['name'])

if __name__ == '__main__':
    manager.run()
