#coding:utf-8
#基础模型类
import datetime
import uuid
from main.extensions import db,whooshee
from werkzeug.security import generate_password_hash, check_password_hash#密码验证
from flask_login import UserMixin
from geoalchemy2 import Geometry
from sqlalchemy import Column, Integer, String
from flask_security import RoleMixin
from flask import url_for
import json
from flask_login import current_user
#geo模型

class Admin(db.Model,UserMixin):#用户模型（管理员权限）
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20))#用户名
    password_hash=db.Column(db.String(128))#密码
    name=db.Column(db.String(100))#用户名称
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        print([self.password_hash,password])
        return check_password_hash(self.password_hash, password)

class _File(db.Model):#文件模型
    id=db.Column(db.Integer,primary_key=True)
    describertion=db.Column(db.String(100))#文件描述
    time=db.Column(db.DateTime)
    uid=db.Column(db.String(60))#唯一值
    path=db.Column(db.String(100))#存放路径
    def __init__(self):
        self.uid=uuid.uuid4()
# 关联表
roles_permissions = db.Table('roles_permissions',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'))
                             )
roles_menus=db.Table('roles_menus',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('menu', db.Integer, db.ForeignKey('menu.id'))
                             )
roles_imgs=db.Table('roles_imgs',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('img', db.Integer, db.ForeignKey('img.id'))
                             )
roles_lines=db.Table('roles_lines',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('line', db.Integer, db.ForeignKey('line.id'))
                             )
roles_points=db.Table('roles_points',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('point', db.Integer, db.ForeignKey('point.id'))
                             )
roles_layers=db.Table('roles_layers',
                             db.Column('role_id', db.Integer, db.ForeignKey('role.id')),
                             db.Column('layer', db.Integer, db.ForeignKey('layer.id'))
                             )
class Permission(db.Model):
    __tablename__ = 'permission'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    roles = db.relationship('Role', secondary=roles_permissions, back_populates='permissions')

# 菜单表
class Menu(db.Model):
    __tablename__ = 'menu'
    id = db.Column(db.Integer, primary_key=True)
    code=db.Column(db.String(50))#代号
    name = db.Column(db.String(50))
    icon = db.Column(db.String(50))
    url = db.Column(db.String(250))
    order = db.Column(db.SmallInteger, default=0)
    roles=db.relationship('Role',secondary=roles_menus,back_populates='menus')#多对多关系建立之后要在下级的class中声明该字段
    secondmenus=db.relationship('SecondMenu',cascade='all')#一对多
    def __str__(self):
        return self.name
#二级菜单类
class SecondMenu(db.Model):
    __tablename__ = 'secondmenu'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    icon = db.Column(db.String(50))
    url = db.Column(db.String(250))
    order = db.Column(db.SmallInteger, default=0)
    menu_id=db.Column(db.Integer,db.ForeignKey('menu.id'))
class Role(db.Model,RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    users = db.relationship('User', cascade='all',back_populates='role')
    permissions = db.relationship('Permission', cascade='all',secondary=roles_permissions, back_populates='roles')
    menus=db.relationship('Menu',cascade='all', secondary=roles_menus, back_populates='roles')
    imgServers=db.relationship('ImgServer',cascade='all', secondary=roles_imgs, back_populates='roles')#角色与创建的影像服务是多对多关系
    lines=db.relationship('Line',cascade='all', secondary=roles_lines, back_populates='roles')
    points=db.relationship('Point',cascade='all', secondary=roles_points, back_populates='roles')
    layers=db.relationship('Layer',cascade='all', secondary=roles_layers, back_populates='roles')
    def __str__(self):
        return str(self.name)
    #获取服务名-服务对象键值对
    def getImgDic(self):
        dic={}
        imgs=self.imgServers
        for img in imgs:
            dic[img.name]=img
        return dic
    #获取图层-图层id键值对
    def getLayerDic(self):
        layerMenus=self.getLayers()
        layerDic={}
        for layerMenu in layerMenus:
            layerDic[layerMenu['name']]=layerMenu['id']
        return layerDic
    #查询该角色管理的图层
    def getLayers(self):
        layers=db.session.query(Layer).filter(Layer.roles.contains(self)).all()
        layerMenus=[]
        for layer in layers:
            layerMenus.append({
                "name":layer.name,
                "id":layer.id
            })
        return layerMenus
    #查询该角色管理的矢量数据
    def getGeoMenus(self):
        geos=[]
        lines=db.session.query(Line).filter(Line.roles.contains(self)).all()
        pts=db.session.query(Point).filter(Point.roles.contains(self)).all()
        geos.extend(lines)
        geos.extend(pts)
   
        geoIndex=[]
        for geo in geos:
            geoIndex.append({
                "name":geo.name,
                "uid":geo.uid
            })
        return geoIndex
    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)
    @staticmethod
    def init_role(config):#静态方法，建立与角色的多对多关系
        menuMap=config.MenuMap
        roles_permissions_map = {
            'User': ['Add', 'Delete', 'Update', 'Query', 'Import', 'Save', 'Export', 'Publish'],
            'Administrator': ['Add', 'Delete', 'Update', 'Query', 'Import', 'Save', 'Export', 'Publish', 'Setting']
        }
        roles_menus_map= {
                'User': ['首页','数据抓取', '数据对比', '影像地图', '矢量地图', '添加数据'],
                'Administrator': ['首页','数据抓取', '数据对比', '影像地图', '矢量地图', '添加数据', '设置']
            }
        for role_name in roles_permissions_map:
            role = Role.query.filter_by(name=role_name).first()
            if role is None:
                role = Role(name=role_name)
                db.session.add(role)
            role.permissions = []
            for permission_name in roles_permissions_map[role_name]:#初始化权限表
                permission = Permission.query.filter_by(name=permission_name).first()
                if permission is None:
                    permission = Permission(name=permission_name)
                    db.session.add(permission)
                role.permissions.append(permission)
            order=0
            for menu_name in roles_menus_map[role_name]:#初始化menu
                menu = Menu.query.filter_by(name=menu_name).first()
                if menu is None:
                    menuConfig=menuMap[menu_name]
                    menu = Menu(id=menuConfig['order'],code=menuConfig['code'],name=menu_name,order=menuConfig['order'],url=menuConfig['url'],icon=menuConfig['icon'])
                    
                    childs=menuConfig['childs']#获取子菜单配置
                    if len(childs)>0:
                        for child in childs:
                            secondMenu=SecondMenu(name=child['name'],order=child['order'],icon=child['icon'],url=child['url'])
                            db.session.add(secondMenu)
                            menu.secondmenus.append(secondMenu)#将该二级菜单加到对应的一级菜单中
                    db.session.add(menu)
                role.menus.append(menu)
                order=order+1
        db.session.commit()
@whooshee.register_model('name', 'username')
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, index=True)   
    password = db.Column(db.String(128))
    name = db.Column(db.String(30))
    confirmed = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role',cascade='all', back_populates='users')
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.set_role('User')
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def set_role(self,role):
        if role is None:
            self.role = Role.query.filter_by(name='User').first()
            # db.session.commit()
        else:
            self.role = Role.query.filter_by(name=role).first()
            # db.session.commit()
    def __str__(self):
        return str(self.name)
    def validate_password(self, password):
        if(check_password_hash(self.password, password) or self.password==password):#搞清楚xadmin为什么存储的是明文密码后把这个改了
            return True
        else:
            return False
    def has_role(self,role):
        return self.role.name == role
    @property
    def is_admin(self):
        return self.role.name == 'Administrator'
    @property
    def is_active(self):
        return self.active
    def can(self, permission_name):
        permission = Permission.query.filter_by(name=permission_name).first()
        return permission is not None and self.role is not None and permission in self.role.permissions
#成果模型，与角色是多对一的关系
class Task(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128))#任务名称
    create_time=db.Column(db.DateTime,default=datetime.datetime.now())

#空间表
class GeoBase():
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128))
    create_user=db.Column(db.String(128))
    style=db.Column(db.String(1024))#矢量样式
    uid=db.Column(db.String(128))#图层唯一值id
    create_time=db.Column(db.DateTime)
    isDel=db.Column(db.Integer,default=1)#是否删除 1未删除，0删除
# @whooshee.register_model('name')
#geo模型
class Point(GeoBase,db.Model):
    roles=db.relationship('Role',secondary=roles_points,back_populates='points')#可查看该服务的用户角色
    geo=db.Column(Geometry('POINT'))
    layer_id=db.Column(db.Integer,db.ForeignKey('layer.id'))
    def __init__(self, *args, **kwargs):
        super(Point, self).__init__(*args, **kwargs)
        self.uid=uuid.uuid4()
        self.create_time=datetime.datetime.now()
        self.create_user=current_user.name
    def getFields(self):
        return ['name','create_user','style','uid','create_time']
    def hasField(self,field):#判断是否含有该字段
        return field in self.getFields()
    def __getitem__(self,k):
        if(k=='name'):
            return self.name
        if(k=='create_user'):
            return self.create_user
        if(k=='style'):
            return self.style
        if(k=='uid'):
            return self.uid
        if(k=='create_time'):
            return self.create_time
    def setProperties(self,properties):#快速设置属性
        keys=properties.keys()
        for key in keys:
            if(self.hasField(key)):
                self[key]=properties[key]
        return self
    def toGeoJson(self):
        geojson=db.session.execute(self.geo.ST_AsGeoJSON()).scalar()
        feature={
            "type": "Feature",
            "geometry": json.loads(geojson),
            "properties": {
            }
        }
        fields=self.getFields()
        for field in fields:
            feature["properties"][field]=str(self[field])
        return feature
# @whooshee.register_model('name')
class Line(GeoBase,db.Model):
    geo=db.Column(Geometry('LINESTRING'))
    roles=db.relationship('Role',secondary=roles_lines,back_populates='lines')#可查看该服务的用户角色
    layer_id=db.Column(db.Integer,db.ForeignKey('layer.id'))
    def __init__(self, *args, **kwargs):
        super(Line, self).__init__(*args, **kwargs)
        self.uid=uuid.uuid4()
        self.create_time=datetime.datetime.now()
        self.create_user=current_user.name
    def getFields(self):
        return ['name','create_user','style','uid','create_time']
    def hasField(self,field):#判断是否含有该字段
        return field in self.getFields()
    def __getitem__(self,k):
        if(k=='name'):
            return self.name
        if(k=='create_user'):
            return self.create_user
        if(k=='style'):
            return self.style
        if(k=='uid'):
            return self.uid
        if(k=='create_time'):
            return self.create_time
    def setProperties(self,properties):#快速设置属性
        keys=properties.keys()
        for key in keys:
            if(self.hasField(key)):
                self[key]=properties[key]
        return self
    def toGeoJson(self):
        geojson=db.session.execute(self.geo.ST_AsGeoJSON()).scalar()
        feature={
            "type": "Feature",
            "geometry": json.loads(geojson),
            "properties": {
            }
        }
        fields=self.getFields()
        for field in fields:
            feature["properties"][field]=str(self[field])
        return feature
#地图服务
class ImgServer(db.Model):
    __tablename__ = 'img'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128))#服务别名
    url=db.Column(db.String(556))#服务地址（wms或其他）
    wmtsUrl=db.Column(db.String(556))#服务地址(wmts)
    tmsUrl=db.Column(db.String(556))#服务地址(tms)
    create_user=db.Column(db.String(56))#创建用户名称
    create_time=db.Column(db.DateTime,default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    roles=db.relationship('Role',secondary=roles_imgs,back_populates='imgServers')#可查看该服务的用户角色\
    bounds=db.Column(db.String(256))#范围，经度纬度之间用,隔开，点之间用空格隔开
#图层模型
class Layer(db.Model):
    __tablename__ = 'layer'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128))#图层名称
    uid=db.Column(db.String(128))#唯一值
    lines=db.relationship('Line')
    points=db.relationship('Point')
    create_user=db.Column(db.String(56))#创建用户名称
    create_time=db.Column(db.DateTime)
    roles=db.relationship('Role',secondary=roles_layers,back_populates='layers')#可查看该服务的用户角色
    #获取所有的要素
    def getFeatures(self):
        feas=[]
        feas.extend(self.points)
        feas.extend(self.lines)
        return feas
    #将图层对象转化成geojson
    def toGeoJson(self):
        features=[]
        for line in lines:
            feature=line.toGeoJson()
            features.append(feature)
        for pt in points:
            feature=pt.toGeoJson()
            features.append(feature)
        featureCollection={
            "type":"FeatureCollection",
            "features":features
        }
        return json.dumps(featureCollection)


#留言
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100))
    body = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, default=datetime.datetime.now(), index=True)
