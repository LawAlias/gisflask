from flask import Flask, current_app
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import RoleMixin, SQLAlchemyUserDatastore, UserMixin, utils

from flask_xadmin.xadm_lib import xModelView, xFileAdmin
from flask_xadmin.xadm_salib import Password
from flask_xadmin import xadm_app, gen_xadmin
from main import app
from main.models import User,Role,Menu,Permission
from main.extensions import db
class myModelView(xModelView):
    column_exclude_list = 'password'
    # Customize your generic model -view
    pass

class myFileAdmin(xFileAdmin):
    def doc(self):
        return "Various files"
    # Customize your File Admin model -view
    pass

# Prepare view list
views = [
    myModelView(model=User, session=db.session, category='Entities'),
    myModelView(model=Role, session=db.session, category='Entities'),
    myFileAdmin(base_path='.', name="Files", category='Files')]

# Make an instance of flask-xadmin
xadmin_obj = gen_xadmin(app = app, title = 'xAdmin', db=db, user_model=User, role_model=Role, views=views)

@app.route('/xadmin/')
def xadmin():
    return redirect('/xadmin/')