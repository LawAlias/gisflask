#coding:utf-8
from main.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash#密码验证
from flask_login import UserMixin
from models import _File,Admin
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String,Float,DateTime
#临时禁飞区模型
class NO_FLYREGION(db.Model):
    gid=db.Column(db.Integer,primary_key=True)
    is_enable=db.Column(db.String(32))
    start_time=db.Column(db.DateTime)
    end_time=db.Column(db.DateTime)
    reg_name=db.Column(db.String(256))
    reg_radius=db.Column(db.Float)
    remark=db.Column(db.String(256))
    valid_time=db.Column(db.String(128))
    reg_gov=db.Column(db.String(256))
    reg_type=db.Column(db.Integer)
    reg_cpoint=db.Column(db.String(64))
    guid=db.Column(db.String(256))
    law_url=db.Column(db.String(256))
    geo=db.Column(Geometry('Polygon'))

