# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import sys
basedir = os.path.dirname(__file__)
class BaseConfig(object):
    SECRET_KEY = os.getenv('SECRET_KEY', 'jsdcdskcndscn')

    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    UPLOADED_PATH=os.path.join(basedir, 'uploads')
    EXTRACT_PATH=os.path.join(basedir, 'extract')
    DROPZONE_ALLOWED_FILE_CUSTOM=True
    DROPZONE_ALLOWED_FILE_TYPE='default,.rar,.zip,.kml'
    DROPZONE_MAX_FILE_SIZE=5000  # set max size limit to a large number, here is 1024 MB
    DROPZONE_TIMEOUT=5 * 60 * 1000  # set upload timeout to a large number, here is 5 minutes
    DROPZONE_UPLOAD_ON_CLICK=True#点击之后才上传
    BLUELOG_POST_PER_PAGE = 10
    BLUELOG_MANAGE_POST_PER_PAGE = 15
    BLUELOG_COMMENT_PER_PAGE = 15
    BLUELOG_SLOW_QUERY_THRESHOLD = 1
    XADMIN_ROLE='Administrator'
    XADMIN_EDIT_ROLE='Administrator'

    #菜单和二级菜单
    MenuMap={
        '首页':{
            'name':'首页',
            'childs':[
            ],
            'url':'map',
            'order':0,
            'icon':'',
            'code':'data'
        },
        '数据对比':{
            'name':'数据对比',
            'childs':[],
            'url':'map',
            'order':1,
            'icon':'',
            'code':'dataCompare'
        },
        '影像地图':{
            'name':'影像地图',
            'childs':[],
            'url':'map',
            'order':2,
            'icon':'',
            'code':'imgMap'
        },
        '矢量地图':{
            'name':'矢量地图',
            'childs':[],
            'url':'map',
            'order':3,
            'icon':'',
            'code':'vecMap'
        },
        '添加数据':{
            'name':'添加数据',
            'childs':[
                {
                    'name':'发布服务',
                    'url':'uploadImg',
                    'icon':'',
                    'order':0
                },
                {
                    'name':'导入矢量数据',
                    'url':'vectorImport',
                    'icon':'',
                    'order':1
                }
            ],
            'url':'map',
            'order':4,
            'icon':'',
            'code':'dataAdd'
        },
        '设置':{
            'name':'设置',
            'childs':[],
            'url':'map',
            'order':5,
            'icon':'',
            'code':'Set'
        },
        '数据抓取':{
            'name':'数据抓取',
            'childs':[
               {
                'name':'高德POI数据抓取',
                'url':'gaode',
                'order':1,
                'icon':''
                }
            ],
            'url':'map',
            'order':6,
            'icon':'',
            'code':'dataGet'
        }
    }
class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = ""#postgresql(安装了postgis扩展)的连接字符串，例如：postgresql://(user):(password)@(ip):(port)/(database)
    GEOSERVERDATAPATH="/Applications/GeoServer.app/Contents/Java/data_dir/data/raster/rh/"#geoserver服务数据存放地址
    SERVERURL="http://localhost:8080/geoserver/"#geoserver基地址
    SERVERNAME="admin"
    SERVERPWD="geoserver"
class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = ""
    GEOSERVERDATAPATH="/Applications/GeoServer.app/Contents/Java/data_dir/data/raster/rh/"#geoserver服务数据存放地址
    SERVERURL="http://localhost:8080/geoserver/"#geoserver基地址
    SERVERNAME="admin"
    SERVERPWD="geoserver"
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}