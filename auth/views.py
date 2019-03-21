#coding:utf-8
from flask import flash,render_template,redirect,url_for
from flask_login import login_user, logout_user, login_required, current_user
from main.forms import LoginForm
from auth import app
from main.models import User
from main.utils import redirect_back
@app.route('/auth',methods=['GET','POST'])
def module1():
    return ('module1 load success')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('map'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        if user is not None and user.validate_password(form.password.data):
            if login_user(user, form.remember_me.data):
                flash('登陆成功.', 'info')
                return redirect_back()
            else:
                flash('您的账户为空.', 'warning')
                return redirect(url_for('map'))
        flash('无效的账户或密码.', 'warning')
    return render_template('auth/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出登录成功.', 'info')
    return redirect_back()