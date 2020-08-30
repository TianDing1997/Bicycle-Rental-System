#views.py保存应用的路由
from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from .. import db
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])#注意导入了auth蓝本，所以使用auth
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):#调用app/model.py中的User类中的verify_password()函数，验证密码是否输入一致
            login_user(user, form.remember_me.data)#login_user在用户会话中标记为已登陆，p85,把用户的ID以字符串的形式写入用户回话
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')#main是因为index调用了main蓝本,url_for(相当于返回了一个地址)
            return redirect(next)
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required#保护路由，禁止未授权的用户访问
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('main.index'))#url_for操作对象是函数，而不是route里的路径。

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account', #调用email中的send-email函数
                    'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')

        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed: #class User中的confirmed属性如果已经为True则直接返回主页面
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))

#过滤未确认的账户
@auth.before_app_request
def before_app_request():
    if current_user.is_authenticated:
        current_user.ping()
        if  not current_user.confirmed \
                and request.endpoint \
                and request.blueprint != 'auth' \
                and request.endpoint != 'static':      #endpoint：处理请求的Flask端点的名称：Flask把视图函数的名称用作路由端点的名称
                        return redirect(url_for('auth.unconfirmed'))

#如果用户未确认邮件则会显示的unconfirmed界面
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:#is_anonymous匿名用户返回True,如果用户为注册或者是已经验证身份则返回主页面
     return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))
