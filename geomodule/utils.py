#-*-coding:utf8-*-
import shapefile
import codecs
from json import dumps
import json
import datetime  
from geoalchemy2.functions import GenericFunction
from fastkml import kml
from fastkml import geometry
from osgeo import ogr
from shapely.geometry import mapping
geofunc=GenericFunction()
class DateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, datetime.date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj) 
#使用ogr读取kml
class KMLDeal():
    #file：文件
    def __init__(self,file):
        self.file=file
    #获取geometry的类型
    def getGeoType(self,geom):
        if isinstance(geom, geometry.Point):
            return "Point"
        elif isinstance(geom, geometry.LinearRing):
            return "LinearRing"
        elif isinstance(geom, geometry.LineString):
            return "LineString"
        elif isinstance(geom, geometry.Polygon):
            return "Polygon"
        elif isinstance(geom, geometry.MultiPoint):
            return "MultiPoint"
        elif isinstance(geom, geometry.MultiLineString):
            return "MultiLineString"
        elif isinstance(geom, geometry.MultiPolygon):
            return "MultiPolygon"
        elif isinstance(geom, geometry.GeometryCollection):
            return "GeometryCollection"
        else:
            raise ValueError("kml中包含无效的geometry类型.")
    #读取geometry数据
    def kmlRead(self):
        file=self.file
        results=[]
        driver = ogr.GetDriverByName('KML')
        dataSource = driver.Open(file)
        layer = dataSource.GetLayer()
        featuredefn = layer.GetLayerDefn()#获取图层属性表定义
        fieldcount = featuredefn.GetFieldCount()#获取属性表中字段数
        for attr in range(fieldcount):
            fielddefn = featuredefn.GetFieldDefn(attr)
        print("%s:  %s"%(\
            fielddefn.GetNameRef(),\
            fielddefn.GetFieldTypeName(fielddefn.GetType())))
        for id, feat in enumerate(layer):
            print(feat.items())
            geom = feat.geometry().Clone()
            if(geom.IsValid()):
                print(fieldcount)
                geotype=geom.GetGeometryName()
                wkt=geom.ExportToWkt()
                result={
                    "wkt":wkt,
                    "geotype":geotype
                }
                results.append(result)
        return results
    #读取placemark属性
    def readPlaceMark(self,placemark):
        data=placemark.extended_data
        geom=placemark.geometry
        geoType=self.getGeoType(geom)
        properties={}
        for ele in data.elements:
            name=ele.name
            value=ele.value
            properties[name]=value
        result={
            "type": "Feature",
            "geometry": json.dumps(mapping(geom)),
            "properties": properties
        }
        return result
    #读取folder属性
    def readFolder(self,folder):
        folderresults=[]
        for placemark in folder.features():
            folderresults.append(self.readPlaceMark(placemark))
        return folderresults
    #读取kml的extenddata即属性和样式
    def getFeatureCollFromKml(self):
        file=self.file
        with open(file,'rt') as f:
            doc=f.read()
            # Create the KML object to store the parsed result
            k = kml.KML()
            # Read in the KML string
            k.from_string(doc)
            results=[]
            for doc in list(k.features()):
                if isinstance(doc,kml.Document):
                    for folder in list(doc.features()):
                        results.extend(self.readFolder(folder))
                elif isinstance(doc,kml.Folder):
                    results.extend(self.readFolder(doc))
                elif isinstance(doc,kml.Placemark):
                    results.extend(self.readPlaceMark(doc))
        FeatureCollection={ 
            "type": "FeatureCollection",
            "features":results
        }
        print(FeatureCollection)
        return FeatureCollection
# read the shapefile
def shp2geo(file):
    reader = shapefile.Reader(file)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    for sr in reader.shapeRecords():
        record = sr.record
        record = [r.decode('gbk', 'ignore') if isinstance(r, bytes)
                  else r for r in record]
        atr = dict(zip(field_names, record))
        geom = sr.shape.__geo_interface__
        buffer.append(dict(type="Feature", geometry=geom, properties=atr))
    geojson = codecs.open(file.split('.')[0] + ".geojson", "w", "utf-8")
    data_json=json.dumps({"type": "FeatureCollection", "features": buffer}, indent=2,cls=DateEncoder)
    data_json.replace('u\'','\'')
    data_json=data_json.decode("unicode-escape") #将unicode编码转化为中文
    geojson.write(data_json+ "\n")
    geojson.close()

def shp2geo_nowriter(file):
    reader = shapefile.Reader(file)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    buffer = []
    geotype=''
    print(reader.shapeRecords())
    for sr in reader.shapeRecords():
        record = sr.record
        record = [r.decode('gbk', 'ignore') if isinstance(r, bytes)
                  else r for r in record]
        atr = dict(zip(field_names, record))
        geom = sr.shape.__geo_interface__
        geotype=geom['type']
        buffer.append(dict(type="Feature", geometry=geom, properties=atr))
    geojson=json.dumps({"type": "FeatureCollection", "features": buffer},cls=DateEncoder)
    geojson.replace('u\'','\'')
    geojson=geojson.decode("unicode-escape")
    return geojson,geotype
def shp2geometry(file):
    reader = shapefile.Reader(file)
    fields = reader.fields[1:]
    field_names = [field[0] for field in fields]
    geotype=''
    geom={}
    for sr in reader.shapeRecords():
        record = sr.record
        record = [r.decode('gbk', 'ignore') if isinstance(r, bytes)
                  else r for r in record]
        atr = dict(zip(field_names, record))
        geom = sr.shape.__geo_interface__
        geotype=geom['type']
    # geojson=json.dumps(geom,cls=DateEncoder)
    # geojson.replace('u\'','\'')
    # geojson=geojson.decode("unicode-escape")
    return geom,geotype
#geojson(geometry)转wkt
def geojson2wkt(geojson):
    if geojson['type']=="Point":
        coordinates=geojson['coordinates']
        return 'POINT({0} {1})'.format(coordinates[0],coordinates[1]),"Point"
    elif geojson['type']=="LineString":
        coordinates=geojson['coordinates']
        line="{0} {1}".format(coordinates[0][0],coordinates[0][1])
        del coordinates[0]
        for coor in coordinates:
            coor="{0} {1}".format(coor[0],coor[1])
            line="{0},{1}".format(line,coor)
        return 'LINESTRING({0})'.format(line),"LINESTRING"
    elif geojson['type']=="Polygon":
        return ' ',"Polygon"
    return " "," "
#shp转换成wkt格式数据
def shp2wkt(file):
    geometry,geotype=shp2geometry(file)
    print(geotype)
    if geotype=="Point":
        coordinates=geometry['coordinates']
        return 'POINT({0} {1})'.format(coordinates[0],coordinates[1]),geotype
    elif geotype=="LINESTRING":
        coordinates=geometry['coordinates']
        line="{0} {1}".format(coordinates[0],coordinates[1])
        del coordinates[0]
        for coor in coordinates:
            coor="{0} {1}".format(coor[0],coor[1])
            line="{0},{1}".format(line,coor)
        return 'LINESTRING({0})'.format(line),geotype
    return " ",geotype
        

