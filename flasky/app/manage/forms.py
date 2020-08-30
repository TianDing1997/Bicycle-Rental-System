from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from ..models import Role, User
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField,FileAllowed,FileRequired
from flask_uploads import UploadSet,IMAGES

photos = UploadSet('photos',IMAGES)

class AddBike(FlaskForm):
    type = SelectField(u'选择车型:', choices=[('山地车', '山地车'), ('公路车', '公路车')])
    brand = StringField(u'输入品牌:', validators=[DataRequired()])
    number = IntegerField(u'输入数量', validators=[DataRequired()])
    rent_price = StringField(u'输入租金(/hour):', validators=[DataRequired()])
    photo = FileField(u'上传图片:',validators=[FileRequired('请选择文件'),FileAllowed(photos,'只能上传图片类型')])
    submit = SubmitField('添加')

class DeleteBike(FlaskForm):
    number = IntegerField(u'输入编号', validators=[DataRequired()])
    submit = SubmitField('删除')

class ChangeBike(FlaskForm):
    number = IntegerField(u'更改编号', validators=[DataRequired()])
    type = SelectField(u'选择车型:', choices=[('山地车', '山地车'), ('公路车', '公路车')])
    brand = StringField(u'输入品牌:', validators=[DataRequired()])
    number = IntegerField(u'输入数量', validators=[DataRequired()])
    rent_price = StringField(u'输入租金(/hour):', validators=[DataRequired()])
    photo = FileField(u'上传图片:',validators=[FileRequired('请选择文件'),FileAllowed(photos,'只能上传图片类型')])
    submit = SubmitField('更改')

class SearchBike(FlaskForm):
    key_type = SelectField(u'关键字类型', choices=[('车型', '车型'), ('品牌', '品牌'), ('租金','租金')])
    key_word = StringField(u'关键字', validators=[DataRequired()])
    submit = SubmitField('查询')
