#coding:utf-8
import os
import flask
import flask_login
from login import app,users
from flask import render_template,flash
from extensions import login_manager
from main.utils import log
import sys
reload(sys)
sys.setdefaultencoding('utf8')
class User(flask_login.UserMixin):
    pass
@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['password'] == users[email]['password']

    return user
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return render_template('login.html')

    email = flask.request.form['email']
    if flask.request.form['password'] == users[email]['password']:
        flash('登陆成功')
        user = User()
        user.id = email
        flask_login.login_user(user)
        
        return flask.redirect(flask.url_for('protected'))
    else:
        flash('登陆失败')
        return 'Bad login'


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id

@app.route('/logout')
def logout():
    flask_login.logout_user()
    return 'Logged out'

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized'