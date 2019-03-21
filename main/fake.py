#coding:utf-8
#生成初始数据、
import models
from main.extensions import db
from sqlalchemy.exc import IntegrityError
def initData():
    # initAdmin()
    initUser()
    # initSingleUser
#管理员
def initAdmin():
    admin=models.Admin(
        id=2,
        username="jin2",
        name="管理员"
    )
    admin.set_password('123')
    db.session.add(admin)
    db.session.commit()
#生成一个测试用户，普通权限
def initUser():
    user = models.User(
        id=2,
        username="jin2",
        name="测试管理员用户",
        confirmed=True
    )
    user.set_password('123')
    user.set_role('Administrator')
    db.session.add(user)
    user2 = models.User(
        id=3,
        username="ucare",
        name="云世纪GIS",
        confirmed=True
    )
    user2.set_password('123')
    user2.set_role('Administrator')
    db.session.add(user2)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        #生成一个测试用户，普通权限
def initSingleUser():
    user = models.User(
        id=3,
        username="jin",
        name="测试普通用户",
        confirmed=True
    )
    user.set_password('123')
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
# def initRole():
#     roles=app.config['ROLES_MENUS_MAP'].keys()
#     for(i=0;i<roles.length;i++):
#         role=models.Role(
#             id=i,
#             name=roles[i],

#         )
# def initMenu():
#     menus=['数据', '数据对比', '影像地图', '矢量地图', '坐标导入', '添加数据', '保存数据', '设置']
#     for (i=0;i<len(menus);i++):
#         menu=models.Menu(
#             id=i,
#             name=menus[i],

#         )