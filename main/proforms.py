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
from flask_login import current_user
from wtforms.fields.html5 import DateField
class PolyLineForm(FlaskForm):
    name=StringField('名称', validators=[DataRequired(), Length(1, 128)])
    
    lineSubmit=SubmitField('保存并关闭')
class POIForm(FlaskForm):
    key=StringField('开发者key',default='2fa236c5584aaeca57b0ad25ab406c86',validators=[DataRequired()])
    keywords=StringField('关键词',validators=[DataRequired()])
    city=StringField('城市',validators=[DataRequired()])
    offset=StringField('最大数量',validators=[DataRequired()])
    poiSubmit=SubmitField('查询')
#图层表单
class LayerForm(FlaskForm):
    layerName = StringField('图层名称', validators=[DataRequired(), Length(1, 70)])
    layerSubmit = SubmitField('确定')
class LayerSelectForm(FlaskForm):
    layerSelect=SelectField(label="选择导入图层",
            validators=[DataRequired("请选择导入图层")],
            coerce=int,
            render_kw={"class": "form-control"})
    layerSubmit=SubmitField('上传')
    def __init__(self, *args, **kwargs):
        super(LayerSelectForm, self).__init__(*args, **kwargs)
        layerDics=current_user.role.getLayers()
        self.layerSelect.choices = [(layerDics.index(layer)+1,layer['name'])#设置图层选项
                                 for layer in layerDics]
   
       
# class No_FlyRegionForm(FlaskForm):
 
#     is_enable
#     start_time
#     end_time
#     reg_name
#     reg_radius
#     remark
#     valid_time
#     reg_gov
#     reg_type
#     reg_cpoint
#     guid
#     law_url
