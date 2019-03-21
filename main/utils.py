# -*- coding: utf-8 -*-
"""
    辅助方法
"""
import zipfile
import os
import exifread
import urllib
from main import app
import logging
import time
import uuid
import xml.sax
from geoserver.catalog import Catalog
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin

from flask import request, redirect, url_for, current_app
#获取文本内容
def getTxtContent(filepath):
    with open(filepath,"r") as f:    #设置文件对象
        str = f.read()
        print("日志内容")
        print(str)
        return str
    return "无"
# 遍历指定目录，显示目录下的所有文件名
def eachFile(filepath):
    files=[]
    pathDir =  os.listdir(filepath)
 
    for allDir in pathDir:
        child = os.path.join(filepath, allDir)
        files.append(child)
    return files
#获取唯一值
def getUid():
    return uuid.uuid1()
#中文字符解译
def decodeCN(jsonData):
    jsonData=json.dumps(jsonData)
    jsonData.replace('u\'','\'')
    jsonData=jsonData.decode("unicode-escape")
    return jsonData
#获取当前时间
def getCurrTime():
    currtime=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    return currtime

 #获取当前时间,精确到时分秒
def getCurrOClock():
    currtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    return currtime
#创建日志对象
def initLog():
    # 创建一个logger
    currtime=getCurrTime()
    logger = logging.getLogger('{0}logger'.format(currtime))
    logger.setLevel(logging.DEBUG)

    # 创建一个handler，用于写入日志文件
    fh = logging.FileHandler('main/log/{0}.log'.format(currtime))
    fh.setLevel(logging.DEBUG)

    # 再创建一个handler，用于输出到控制台
    # ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # ch.setFormatter(formatter)

    # 给logger添加handler
    logger.addHandler(fh)
    # logger.addHandler(ch)
    return logger

log=initLog()

extract=app.config['EXTRACT_PATH'][0]
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='index', **kwargs):
    print(request.args)
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
#判断文件是否是压缩包
def fileIsZip(file):
    iszip = zipfile.is_zipfile(file)
    return iszip
#解压压缩包文件至指定文件夹，并返回解压后的文件路径
def getExtractedFile(file,extract_path=None):
    if extract_path is None:
        extract_path=extract
    paths=[]
    # 获取压缩包
    fz = zipfile.ZipFile(file, 'r')
    # 遍历压缩包里面的文件
    for file in fz.namelist():
        # 解压文件到指定路径下
        fz.extract(file, extract_path)
        # 拼接成解压后的文件路径
        upload_path = os.path.join(extract_path, file)
        paths.append(upload_path)
    return paths
#获取图片信息 file:图片文件名 
def getPicInfo(file):
    res=[]
    # 读取照片信息
    path=os.path.join(extract_path, file)
    fd = open(path, 'rb')
    # 获取照片的属性组
    tags = exifread.process_file(fd)
    fd.close()
    # 获取照片属性中的创建时间
    if 'Image DateTime' in tags:
        date = str(tags['Image DateTime'])
        LatRef = tags["GPS GPSLatitudeRef"].printable
        Lat = tags["GPS GPSLatitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
        Lat = float(Lat[0]) + float(Lat[1]) / 60 + float(Lat[2]) / float(Lat[3]) / 3600
        if LatRef != "N":
            Lat = Lat * (-1)
        # 经度
        LonRef = tags["GPS GPSLongitudeRef"].printable
        Lon = tags["GPS GPSLongitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
        Lon = float(Lon[0]) + float(Lon[1]) / 60 + float(Lon[2]) / float(Lon[3]) / 3600
        if LonRef != "E":
            Lon = Lon * (-1)
        date1 = date.split(' ')
        date1[0] = date1[0].replace(':', '-')
        date = ' '.join(date1)
        # 文件重命名
        new_name = date.replace(':', '').replace(' ', '_') + os.path.splitext(file)[1]
        tot = 1
        new_upload_path = os.path.join(extract_path, new_name)
        while os.path.exists(new_upload_path):
            new_name = date.replace(':', '').replace(' ', '_')+'_'+str(tot) + os.path.splitext(file)[1]
            tot += 1
            new_upload_path = os.path.join(extract_path, new_name)
        # 重命名文件需要传入的是路径加文件名 ../../1.png, ../../2018_0912.png
        os.rename(path, new_upload_path)
        # 拼接图片存储的URL
        pathName = urllib.pathname2url(new_upload_path)
        path = urlparse.urljoin(request.url[:pos], pathName)
        # 文件名不加后缀
        index = file.rfind('.')
        # 解决获取中文文件名的问题
        describertion = file[:index].decode('GB2312')
        res.append({
            'time': date,
            'describertion': describertion,
            'path': path,
            'pos': [Lat, Lon]
        })
#解压
import zipfile
def decompress(zipFilePath,extractPath):
    try:
        f = zipfile.ZipFile(zipFilePath,'r')
        for file in f.namelist():
            # print(file)
            f.extract(file,extractPath)
        return 'true'
    except Exception, e:
        return 'false'
import os

#删除文件夹下的文件以及子文件夹
def del_file(path):
      for i in os.listdir(path):
         path_file = os.path.join(path,i)#取文件绝对路径
         if os.path.isfile(path_file):
           os.remove(path_file)
         else:
             del_file(path_file)
class Geoserver:
    geourl = "{0}rest".format(app.config['SERVERURL'])  # the url of geoserver
    geocat = Catalog(geourl, username=app.config['SERVERNAME'], password=app.config['SERVERPWD'])  # create a Catalog object
    
    #创建栅格数据存储 name:存储名称，filePath：数据源路径，workSpaceName：工作空间名称
    def createCoverageStore(self,name,filePath,workSpaceName):
        try:
            data_url = 'file:{0}'.format(filePath)
            return self.geocat.create_coveragestore2(name, data_url,workSpaceName)
        except Exception, e:
            log.info("创建{0}栅格数据存储出错：{1}".format(name,str(e)))
            return 'false'
    #创建栅格数据存储并返回服务地址 name:存储名称，filePath：数据源路径，workSpaceName：工作空间名称
    #return wms服务地址和wmts服务地址,bounds:服务的范围
    def createCoverageStoreUrl(self,name,filePath,workSpaceName):
        try:
            data_url = 'file:{0}'.format(filePath)
            self.geocat.create_coveragestore2(name, data_url,workSpaceName)
            url1="{0}{1}/wms".format(app.config['SERVERURL'],workSpaceName)
            layer="{1}:{0}".format(name,workSpaceName)
            url2="{0}gwc/service/wmts?layer={3}%3A{1}&style=&tilematrixset=EPSG%3A900913&Service=WMTS&Request=GetTile&Version=1.0.0&Format=image%2Fpng&{2}".format(app.config['SERVERURL'],name,"TileMatrix=EPSG%3A900913%3A{z}&TileCol={x}&TileRow={y}",workSpaceName)
            bounds=self.getBoundsFromStore(name,workSpaceName)
            return {
                'wms':url1,
                'wmts':url2,
                'bounds':bounds
            }
        except Exception, e:
            log.info("创建{0}栅格数据存储出错：{1}".format(name,str(e)))
            return False
    #查询所有工作空间
    def queryAllWorkSpaces(self):
        try:
            workspaces=self.geocat.get_workspaces()
            return workspaces
        except Exception, e:
            log.info("查询工作空间出错：{0}".format(str(e)))
            return 'false'
    #创建工作空间
    def createWorkSpace(self,name,uri):
        try:
            return self.geocat.create_workspace(name,uri)
        except Exception, e:
            log.info("创建{0}工作空间出错：{1}".format(name,str(e)))
            return 'false'
    #根据数据存储名称和工作空间名称获取资源
    def getResource(self,storeName,workSpaceName=None):
        if workSpaceName is not None:
            return self.geocat.get_resource(storeName,workspace=workSpaceName)
        return self.geocat.get_resource(storeName)
    #根据数据存储名称和工作空间名称获取资源的经纬度范围
    def getBoundsFromStore(self,storeName,workSpaceName=None):
        resource=self.getResource(storeName,workSpaceName)
        return resource.latlon_bbox

# class Kml:
#     class KMLHandler(xml.sax.ContentHandler):
        

        

