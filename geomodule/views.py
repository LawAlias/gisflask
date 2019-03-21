#coding:utf-8
from flask import flash,render_template,request
from geomodule import app
from flask_login import login_required, current_user
import os
from main.utils import getExtractedFile,decompress,del_file,log
from utils import shp2geo_nowriter,geofunc,shp2wkt,geojson2wkt,KMLDeal
from main.utils import getUid,getCurrOClock
from main.models import Point,Line,Layer
import json
from werkzeug.utils import secure_filename
from main.extensions import db
from main.proforms import LayerSelectForm
import datetime
@app.route('/geomodule',methods=['GET','POST'])
def geomodule():
    return ('geomodule load success')
@app.route('/vectorImport',methods=['GET','POST'])
@login_required
def vectorImport():
    # layerSelectForm=LayerSelectForm()
    layerDic=current_user.role.getLayerDic()
    if request.method == 'POST':
        layerName=request.form.get('layerSelect')
        uploadPath=app.config['UPLOADED_PATH']
        for key, f in request.files.items():
            if key.startswith('file'):
                layerId=layerDic[layerName]
                filename=secure_filename(f.filename)
                savePath=os.path.join(uploadPath, filename)
                f.save(savePath)
                extname=os.path.splitext(filename)[1]
                if(extname==".kml"):
                    kml=KMLDeal(savePath)
                    # kml2geo(savePath)
                    wkts=kml.getFeatureCollFromKml()
                    print(wkts)
                    # wktImport(layerId,wkts)
                elif(extname==".geojson"):
                    ll=1
                else:
                    extractPath=os.path.join(uploadPath,'vector',filename)
                    # parentPath=os.path.join(uploadPath,'vector',filename)#上传路径的上级，完事后将这个文件夹删除（否则每次上传一个文件就会产生一个）
                    isExists=os.path.exists(extractPath)#先验证路径是否存在
                    if not isExists:
                        os.mkdir(extractPath)#解压路径不存在则创建
                    deresult=decompress(savePath,extractPath)#得到解压路径
                    if deresult is 'true':#解压成功的话
                        list = os.listdir(extractPath)
                        for i in range(0,len(list)):#遍历
                            path = os.path.join(extractPath,list[i])#组合文件路径
                            if os.path.isfile(path):#如果是个有效文件
                                (filename,pathSp) = os.path.splitext(path)#获取文件名无后缀（暂时没什么用）和后缀名
                                filename=os.path.basename(path)#获取文件名无后缀（这个才有用）
                                if (pathSp=='.shp'):#后缀名
                                    geojson,geoType=shp2geo_nowriter(path)#得到geojson数据
                                    geojsonImport(layerId,geojson,geoType)
        db.session.commit()#循环完所有文件后再提交           
    return render_template('admin/new_shp.html')
#wkt入库，这里的wkt集合是从kml中读取的，和从shp中读取的geojson不同，每个元素类型可能都不同
def wktImport(layerId,wkts):
    print(wkts)
    for wktResult in wkts:
        geoType=wktResult["geotype"]
        wkt=wktResult["wkt"]
        if geoType == 'Point':
            pt=Point(layer_id=layerId,create_user=current_user.name,roles=[current_user.role],geo=wkt)
            db.session.add(pt)
        elif geoType == 'LineString' and geoType == 'LINESTRING':
            line=Line(layer_id=layerId,create_user=current_user.name,roles=[current_user.role],geo=wkt)
            db.session.add(line)
#shp入库
def geojsonImport(layerId,geojson,geoType):
    geojson=json.loads(geojson)
    if geoType == 'Point':
        features=geojson['features'];
        for fea in features:
            geometry=fea['geometry']
            properties=fea['properties']
            geometry,geotype=geojson2wkt(geometry)
            pt=Point(layer_id=layerId,create_user=current_user.name,roles=[current_user.role],geo=geometry)
            pt=pt.setProperties(properties)
            db.session.add(pt)
    elif geoType == 'LineString':
        features=geojson['features'];
        for fea in features:
            geometry=fea['geometry']
            geometry,geotype=geojson2wkt(geometry)
            properties=fea['properties']
            line=Line(layer_id=layerId,create_user=current_user.name,roles=[current_user.role],geo=geometry)
            line=line.setProperties(properties)
            db.session.add(line)
@app.route('/vectoreview',methods=['GET','POST'])
@login_required
def vectoreview():
    # geos=getGeos(current_user.role)
    # geos=json.dumps(geos)
    uid=request.args.get("uid")
    # start_time=getCurrOClock()
    return render_template('map/vectoreview.html',uid=uid,role_id=current_user.role_id)

