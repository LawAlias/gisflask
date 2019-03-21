#coding:utf-8
from flask import request,redirect,render_template,url_for,flash
from main import app,db
from flask_login import current_user
from utils import initLog,eachFile,getTxtContent
import os
from proforms import PolyLineForm,LayerForm,POIForm
from forms import HelloForm
from models import Message
from table import RecycleTable,RecycleItem
@app.route('/',methods=['GET','POST'])
def main():
    return redirect(url_for('map'))
@app.route('/map/',methods=['GET','POST'])
def map():
    if current_user.is_authenticated:
        log=initLog()
        log.info("用户:{0}登陆成功".format(current_user.name))
    else:
        return redirect(url_for('login'))
    lineForm=PolyLineForm()
    lineForm.name(class_='lineform')
    layerform=LayerForm()
    return render_template('map/map.html',form=lineForm,layerform=layerform)
@app.route('/log/',methods=['GET','POST'])
def log():
    filepath=request.args.get("path")
    content="无"
    if(filepath):
        content=getTxtContent(filepath)
    logs=eachFile(os.path.join('main', 'log'))
 
    return render_template('log/loglist.html',logs=logs,content=content)
@app.route('/gaode/',methods=['GET','POST'])
def gaode():
    poiForm=POIForm()
    
    return render_template('map/getpoi.html',form=poiForm)


@app.route('/dataCompare/', methods=['POST', 'GET'])
def dataCompare():
    return render_template('map/map.html')
@app.route('/vectorMap/', methods=['POST', 'GET'])
def vectorMap():
    return render_template('map/map.html')
@app.route('/coorImport/', methods=['POST', 'GET'])
def coorImport():
    return render_template('map/map.html')
@app.route('/dataSave/', methods=['POST', 'GET'])
def dataSave():
    return render_template('map/map.html')
@app.route('/chart/', methods=['POST', 'GET'])
def chart():
    return render_template('charts/chart.html')
@app.route('/table/', methods=['POST', 'GET'])
def table():
    return render_template('charts/chart.html')
@app.route('/messboard/', methods=['GET', 'POST'])
def messboard():
    messages = Message.query.order_by(Message.timestamp.desc()).all()
    form = HelloForm()
    if form.validate_on_submit():
        name=form.name.data
        body = form.body.data
        message = Message(body=body, name=current_user.name+":"+name)
        db.session.add(message)
        db.session.commit()
        flash('你的留言已提交')
        return redirect(url_for('messboard'))
    return render_template('blog/message.html', form=form, messages=messages)
#回收站
@app.route('/recycle/', methods=['GET', 'POST'])
def recycle():
    items = [dict(name='Name1', description='删除'),
         dict(name='Name2', description='删除'),
         dict(name='Name3', description='删除')]
    # # Or, more likely, load items from your database with something like
    # items = RecycleTable.query.all()
    # # Populate the table
    table = RecycleTable(items)
    
    return render_template('tables/recyclebin.html', table=table)