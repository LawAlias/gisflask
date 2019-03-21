#coding:utf-8
from flask import Flask
import os
import click
from extensions import toolbar,bootstrap,db,login_manager,moment,dropzone,whooshee
from main.models import Admin,Menu,Role
from settings import config
from flask_login import current_user
import fake
import sys
from flask_cors import CORS
reload(sys) # Python2.5 初始化后会删除 sys.setdefaultencoding 这个方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')
def create_app(config_name=None):
    if config_name is None:
        config_name=os.getenv('FLASK_CONFIG','development')
    app = Flask('main')
    app.config.from_object(config[config_name])
    register_extensions(app)
    register_template_context(app)
    register_commands(app)
    app.debug=True
    CORS(app, supports_credentials=True)
    return app 
def register_extensions(app):
    toolbar.init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    moment.init_app(app)
    dropzone.init_app(app)
    whooshee.init_app(app)
def register_template_context(app):#模版上下文
    @app.context_processor
    def make_template_context():
        # admin=Admin.query.first()
        layers=[]
        if current_user.is_authenticated:
            menus=current_user.role.menus
            layers=current_user.role.getLayers()
        else:
            menus=['数据']
        # projects=admin.projects
        for menu in layers:
            print(menu)
        return dict(menus=menus,geoMenus=layers,config=app.config)
def register_commands(app):
    #生成数据表
    @app.cli.command()
    @click.option('--drop', is_flag=True, help='Create after drop.')
    def initdb(drop):
        """Initialize the database."""
        if drop:
            click.confirm('This operation will delete the database, do you want to continue?', abort=True)
            db.drop_all()
            click.echo('Drop tables.')
        db.create_all()
        click.echo('Initialized database.')
    #生成数据
    @app.cli.command()
    def initdata():
        Role.init_role(config['development'])#初始化角色
        #生成用户
        fake.initData()
        click.echo('success.')
    #生成管理员
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    @click.option('--password', prompt=True, hide_input=True,
                  confirmation_prompt=True, help='The password used to login.')
    def init(username, password):
        """Building project, just for you."""

        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin is not None:
            click.echo('The administrator already exists, updating...')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                name='Admin'
            )
            admin.set_password(password)
            db.session.add(admin)

        # project = Project.query.first()
        # if project is None:
        #     click.echo('Creating the default project...')
        #     project = Project(name='Default',uid="111",manager_id="1")
        #     db.session.add(project)

        db.session.commit()
        click.echo('Done.')     
app=create_app()
# import login
import utils
import table
import auth
import module2
import geomodule
import apis
import xadmin
from main import views
from main import admin