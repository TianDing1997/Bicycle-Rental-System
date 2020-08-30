from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import Role, User
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField

class PostForm(FlaskForm):
    body = PageDownField("请输入评价", validators=[DataRequired()])
    submit = SubmitField('提交')


#class NameForm(FlaskForm):
#    name = StringField('What is your name?', validators=[DataRequired()])
#    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0,64)])
    location = StringField('地址', validators=[Length(0,64)])
    about_me = TextAreaField('简介')
    submit = SubmitField('提交')

class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-0_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')
    ])
    confirmed = BooleanField('验证状态')
    role = SelectField('角色', coerce=int)#coerce转换为整型, p109
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('简介')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)#继承父类FlaskForm的初始化函数
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]#按角色名的字母顺序排列
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
           raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
           raise ValidationError('Username already in use.')
