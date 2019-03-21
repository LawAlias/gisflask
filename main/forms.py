# -*- coding: utf-8 -*-
"""
表单
"""
from flask_wtf import FlaskForm
from wtforms import MultipleFileField,DateField,DateTimeField,RadioField,IntegerField,StringField, SubmitField, SelectField, TextAreaField, ValidationError, HiddenField, \
    BooleanField, PasswordField
from wtforms.validators import InputRequired,DataRequired, Email, Length, Optional, URL
# from main.models import Task,Project
from flask_wtf.file import FileRequired,FileField,FileAllowed
from utils import Geoserver
from flask_login import current_user
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(1, 128)])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')


#服务发布表单
class PublishForm(FlaskForm):
    serverType=RadioField('选择服务文件类型', choices=[('vec', '矢量'), ('ras', '栅格')],default='ras', validators=[InputRequired(),DataRequired(), Length(1, 60)])
    file=FileField('选择文件压缩包',validators=[FileRequired(),InputRequired(),DataRequired(),FileAllowed(['zip','rar'])])
    workSpaces=SelectField('选择工作空间',validators=[InputRequired(),DataRequired()])
    localTile=BooleanField('切片到本地')
    minZoom=SelectField('切片到本地的最小缩放等级',coerce = int,default=4,validators=[InputRequired(),DataRequired()])
    maxZoom=SelectField('切片到本地的最大缩放等级',coerce = int,default=20,validators=[InputRequired(),DataRequired()])
    submit=SubmitField('开始发布')
    def __init__(self, *args, **kwargs):
        geoserver=Geoserver()
        super(PublishForm, self).__init__(*args, **kwargs)
        self.workSpaces.choices = [(workSpace.name,workSpace.name)
                                 for workSpace in geoserver.queryAllWorkSpaces()]
        
        self.minZoom.choices = [(level,level)
                                 for level in range(1,24)]
        self.maxZoom.choices = [(level,level)
                                 for level in range(1,24)]
#影像比较选择框
class ImgCompareForm(FlaskForm):
    imgLeft=SelectField('比较影像1',coerce = int,validators=[InputRequired(),DataRequired()])
    imgRight=SelectField('比较影像2',coerce = int,validators=[InputRequired(),DataRequired()])
    submit=SubmitField('开始比较')
    def __init__(self, *args, **kwargs):
        super(ImgCompareForm, self).__init__(*args, **kwargs)
        imgServers=current_user.role.imgServers
        print(imgServers)
        self.imgLeft.choices = [(imgServers.index(img)+1,img.name)
                                 for img in imgServers]
        self.imgRight.choices = [(imgServers.index(img)+1,img.name)
                                 for img in imgServers]
class HelloForm(FlaskForm):
    name = StringField('主题', validators=[DataRequired(), Length(1, 20)])
    body = TextAreaField('留言', validators=[DataRequired(), Length(1, 200)])
    submit = SubmitField('提交')