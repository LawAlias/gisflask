#coding:utf-8
import urllib,urllib2
from flask import flash,render_template,request,redirect,url_for
from flask.views import MethodView
from apis import app
from flask_login import login_required, current_user
from geomodule.utils import shp2geo_nowriter,geofunc,shp2wkt,geojson2wkt
from main.utils import getUid,getCurrOClock,log,getCurrTime
from main.models import Point,Line,Role,Layer
from main.proModels import NO_FLYREGION
from main.extensions import db
from main.proforms import POIForm
import json
import uuid
import datetime
@app.route('/apis',methods=['GET','POST'])
def apis():
    return ('apis load success')
#mvc
class LineTest(MethodView):
    def get(self,uid):
        return uid
class LayerFeature(MethodView):
    def get(self,uid):
        try:
            layer=db.session.query(Layer).filter(Layer.uid==uid).first()
            if(layer):
                return layer.toGeoJson()
        except Exception, e:
            log.info("用户{0}查询图层出错：{1},uid参数:{2}".format(current_user.name,str(e),uid))
            return 'False'
    def delete(self,uid):
        try:
            layer=db.session.query(Layer).filter(Layer.uid==uid).first()
            db.session.delete(layer)
            db.session.commit()
            return 'True'
        except Exception, e:
            log.info("用户{0}删除图层出错：{1},uid参数:{2}".format(current_user.name,str(e),uid))
            return 'False'
class LayerFeatures(MethodView):
    decorators=[login_required]
    #查询该角色的所有图层
    def get(self):
        try:
            role=current_user.role
            layers=db.session.query(Layer).filter(Layer.roles.contains(role)).all()
            return json.dumps(layers)
        except Exception, e:
            log.info("用户{0}查询图层出错：{1}".format(current_user.name,str(e)))
            return 'False'
    def post(self):
        name=request.form["name"]
        uid=request.form["uid"]
        try:
            
            layer=db.session.query(Layer).filter(Layer.uid==uid).first()
            if(layer):#如果已存在，那直接修改
             
                layer.name=name
                db.session.commit()
                return "True"
            else:
                roles=[current_user.role]
                new_layer=Layer(name=name,uid=uid,create_user=current_user.name,create_time=getCurrTime(),roles=roles)
                db.session.add(new_layer)
                db.session.commit()
                return "True"
        except Exception, e:
            log.info("用户{0}更新图层出错：{1}，uid参数:{2}".format(current_user.name,str(e),uid))
            return 'False'
        # elif:#否则就是新加或是更改图形
app.add_url_rule('/api/layerfeature/<string:uid>',view_func=LayerFeature.as_view('layerfeature_api'),methods=['GET','DELETE'])
app.add_url_rule('/api/layerfeatures',view_func=LayerFeatures.as_view('layerfeatures_api'),methods=['POST'])
class LineFeature(MethodView):
    def get(self,uid):
        try:
            line=db.session.query(Line).filter(Line.uid==uid).first()
            return json.dumps(line)
        except Exception, e:
            log.info("用户{0}查询要素出错：{1},uid参数:{2}".format(current_user.name,str(e),uid))
            return 'False'
    def delete(self,uid):
        try:
            line=db.session.query(Line).filter(Line.uid==uid).first()
            db.session.delete(line)
            db.session.commit()
            return 'True'
        except Exception, e:
            log.info("用户{0}删除要素出错：{1},uid参数:{2}".format(current_user.name,str(e),uid))
            return 'False'
class LineFeatures(MethodView):
    decorators=[login_required]
    def post(self):
        try:
            geojson=request.form["geojson"]
            layerId=request.form["layerId"]
            geojson=json.loads(geojson)
            if(geojson.has_key('type') and geojson['type']=='FeatureCollection'):
                if geojson.has_key('properties') and geojson['properties'].has_key('uid'):#样式和属性只能针对单个要素修改，所以要求有uid
                    uid=geojson['properties']['uid']
                    line=db.session.query(Line).filter(Line.uid==uid).first()
                    for key in properties.keys():#改属性
                        if(key is not 'style' or key is not 'uid' ):
                            line[key]=properties[key]
                        elif(key is 'style'):
                            styles=json.dumps(properties['style'])
                            print("styles")
                            print(styles)
                            line.style=styles
                    db.session.commit()
                else:
                    for feature in geojson['features']:
                        feaImport(feature,layerId)
                    return 'True'
            else:#否则就是个feature
                feaImport(geojson,layerId)
                return 'True'
        except Exception, e:
            log.info("用户{0}更新要素出错：{1}，json参数:{2}".format(current_user.name,str(e),geojson))
            return 'False'
        # elif:#否则就是新加或是更改图形
app.add_url_rule('/api/linefeature/<string:uid>',view_func=LineFeature.as_view('linefeature_api'),methods=['GET','DELETE'])
app.add_url_rule('/api/linefeatures',view_func=LineFeatures.as_view('linefeatures_api'),methods=['POST'])
#feature入库
def feaImport(feature,layerId):
    geometry=feature['geometry']
    styles=feature['properties']
    fields=feature['properties']['field'] if feature['properties'].has_key('field') else {name:'name'}
    wkt,geoType=geojson2wkt(geometry)
    uid=styles['uid']
    currentime=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if geoType is 'Point':      
        pt=Point(name=fields['name'],uid=uid,create_time=currentime,create_user=current_user.name,style=json.dumps(styles),roles=[current_user.role],geo=wkt)#怎么把geojson转化为geom
        db.session.add(pt)
        db.session.commit()
    elif geoType is 'LINESTRING':
        line=db.session.query(Line).filter(Line.uid==uid).first()
        if(line):
            line.style=json.dumps(styles)
            line.name=fields['name']
            line.geo=wkt
            db.session.commit()
        else:
            new_line=Line(layer_id=layerId,name=fields['name'],uid=uid,create_time=currentime,create_user=current_user.name,style=json.dumps(styles),roles=[current_user.role],geo=wkt)#怎么把geojson转化为geom
            db.session.add(new_line)
            db.session.commit()
    elif geoType is 'Polygon':
        uid=getUid()
        is_enable="1"
        polygon=NO_FLYREGION(guid=uid,is_enable=is_enable,geo=geojson)
@app.route('/api/saveGeo',methods=['POST'])
@login_required
def saveGeo():
    geojson=request.form["geojson"]#FeatureCollection
    geojson=json.loads(geojson)
    for feature in geojson['features']:
        geometry=feature['geometry']
        styles=feature['properties']
        wkt,geoType=geojson2wkt(geometry)
        if geoType is 'Point':       
            pt=Point(name='name',create_user=current_user.name,style=json.dumps(styles),roles=[current_user.role],geo=wkt)#怎么把geojson转化为geom
            db.session.add(pt)
            db.session.commit()
        elif geoType is 'LINESTRING':
            pt=Line(name='name',create_user=current_user.name,style=json.dumps(styles),roles=[current_user.role],geo=wkt)#怎么把geojson转化为geom
            db.session.add(pt)
            db.session.commit()
        elif geoType is 'Polygon':
            uid=getUid()
            is_enable="1"
            polygon=NO_FLYREGION(guid=uid,is_enable=is_enable,geo=geojson)
    flash("保存成功")
    return "success"


@app.route('/api/getGeos',methods=['POST'])
@login_required
#查询该角色管理的矢量数据
def getGeos():
    try:
        geos=[]
        role_id=request.form["role_id"]
        role=db.session.query(Role).filter(Role.id==role_id).first()
        lines=db.session.query(Line).filter(Line.roles.contains(role)).all()
        pts=db.session.query(Point).filter(Point.roles.contains(role)).all()
        geos.extend(lines)
        geos.extend(pts)
        features=[]
        for geo in geos:
            geojson=db.session.execute(geo.geo.ST_AsGeoJSON()).scalar()
            feature={
                "type": "Feature",
                "geometry": json.loads(geojson),
                "properties": {
                    "name": geo.name,
                    "create_user":geo.create_user,
                    "create_time":str(geo.create_time),
                    "uid":geo.uid,
                    "style":geo.style
                }
            }
           
            features.append(feature)
        response={
            "code":200,
            "data":features
        }
        return json.dumps(response)
    except Exception, e:
        log.info("用户{0}获取矢量图层出错：{1}，role_id参数:{2}".format(current_user.name,str(e),role_id))
        return 'False'
@app.route('/api/queryAllLayers',methods=['POST'])
@login_required
#查询所有图层，转化成geojson
def queryAllLayers():
    try:
        role=current_user.role;
        layers=db.session.query(Layer).filter(Layer.roles.contains(role)).all()
        feaCollections=[]
        for layer in layers:
            layer_id=layer.id
            print("layer_id")
            print(layer_id)
            lines=db.session.query(Line).filter(Line.layer_id==layer_id,Line.isDel==0).all()
            pts=db.session.query(Point).filter(Point.layer_id==layer_id,Point.isDel==1).all()
            geos=[]
            geos.extend(lines)
            geos.extend(pts)
            features=[]
            for geo in geos:
                feature=geo.toGeoJson()
                
                features.append(feature)
            feaCollection={
                "type": "FeatureCollection",
                "features":features,
                "properties": {
                    "name": layer.name,
                    "uid": layer.id,
                    "create_time":str(layer.create_time),
                    "create_user":current_user.name
                    }
            }
            feaCollections.append(feaCollection)
        response={
            "code":200,
            "data":feaCollections
        }
        return json.dumps(response)
    except Exception, e:
        log.info("用户{0}获取图层出错：{1}".format(current_user.name,str(e)))
        return 'False'
@app.route('/api/queryAllLayerNames',methods=['POST'])
@login_required
#查询该角色管理的图层名称集合
def queryAllLayerNames():
    try:
        layers=current_user.role.getLayers();
        response={
            "code":200,
            "data":layers
        }
        return json.dumps(response)
    except Exception, e:
        log.info("用户{0}获取图层名称集合出错：{1}".format(current_user.name,str(e)))
        return 'False'
@app.route('/api/getGaodes',methods=['POST'])
def getGaodes():
    key=request.form['key']
    keywords=request.form['keywords']
    city=request.form['city']
    offset=request.form['offset']
    # 爬取数据
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'}
    textmod={'key':key,'keywords':keywords,'city':city,'children':'1','offset':offset,'page':'1','extensions': 'all'}
    textmod = urllib.urlencode(textmod)
    url1 = "http://restapi.amap.com/v3/place/text"
    req = urllib2.Request(url = '%s%s%s' % (url1,'?',textmod))
    res = urllib2.urlopen(req)
    res = res.read()
    # json解析
    datajson = json.loads(res)


    # 名字 位置 地址 电话 区划
    # name location address tel adname

    pois = datajson['pois']
    features=[]
    for i in range(0,len(pois)):
        location=pois[i]['location'].split(',')
        fea={
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(location[0]),
                        float(location[1])
                    ]
                },
                "properties": {
                    "name": pois[i]['name'],
                    "address":pois[i]['address'],
                    "tel":pois[i]['tel'],
                    "adname":pois[i]['adname']
                }
            }
        features.append(fea)
    featureCollection={
        "type":"FeatureCollection",
        "features":features
    }
    featureCollection=json.dumps(featureCollection)

    featureCollection.replace('u\'','\'')

    featureCollection=featureCollection.decode("unicode-escape") 
    return featureCollection


#根据关键词查询要素
@app.route('/api/searchFeature',methods=['POST'])
def searchFeature():
    key=request.form['key']
    print(key)
    if(key==''):
        flash('请输入关键字','warning')
        return redirect(url_for('map'))
    geo=""
    line=db.session.query(Line).filter(Line.name==key).first()
    if(line):
        geo=line.toGeoJson()
    else:
        pt=db.session.query(Point).filter(Point.name==key).first()
        if(pt):
            geo=pt.toGeoJson()
    response={
            "code":200,
            "data":geo
        }
    return json.dumps(response)
    
