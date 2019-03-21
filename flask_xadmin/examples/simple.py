# -*- coding: utf-8 -*-
# __author__ = 'dsedad'

# Flask-xAdmin example
# by Sedad Delalic
# December 20, 2016


from flask import Flask, current_app
from flask import redirect
from flask_sqlalchemy import SQLAlchemy
from flask_security import RoleMixin, SQLAlchemyUserDatastore, UserMixin, utils

from flask_xadmin.xadm_lib import xModelView, xFileAdmin
from flask_xadmin.xadm_salib import Password
from flask_xadmin import xadm_app, gen_xadmin


# Initialize Flask and set some config values
app = Flask(__name__)
app.config['DEBUG']=True
# Replace this with your own secret key
app.config['SECRET_KEY'] = 'super-secret'
# The database must exist (although it's fine if it's empty) before you attempt to access any page of the app
# in your browser.
# I used a PostgreSQL database, but you could use another type of database, including an in-memory SQLite database.
# You'll need to connect as a user with sufficient privileges to create tables and read and write to them.
# Replace this with your own database connection string.
#xxxxx
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///xadmin_demo.db'

# Set config values for Flask-Security.
# We're using PBKDF2 with salt.
app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2_sha512'
# Replace this with your own salt.
app.config['SECURITY_PASSWORD_SALT'] = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# xAdmin roles
app.config['XADMIN_ROLE'] = 'flask-xadmin'
app.config['XADMIN_EDIT_ROLE'] = 'flask-xadmin-edit'

db = SQLAlchemy(app)

# Create a table to support a many-to-many relationship between Users and Roles
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


# Role class
class Role(db.Model, RoleMixin):
    """ Roles """

    # Our Role has three fields, ID, name and description
    id = db.Column(db.Integer(), primary_key=True, doc="Role id")
    name = db.Column(db.String(80), unique=True, doc="Role name")
    description = db.Column(db.String(255), doc="Role description")

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    # If we were using Python 2.7, this would be __unicode__ instead.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


# User class
class User(db.Model, UserMixin):
    """ Application users """
    # Our User has six fields: ID, email, password, active, confirmed_at and roles. The roles field represents a
    # many-to-many relationship using the roles_users table. Each user may have no role, one role, or multiple roles.
    id = db.Column(db.Integer, primary_key=True, doc="id")
    email = db.Column(db.String(255), unique=True, doc="Valid email")
    name = db.Column(db.String(255), doc="Full name")
    password = db.Column(Password(255), doc="Password")
    active = db.Column(db.Boolean(), doc="Only active users are allowed to log in")
    confirmed_at = db.Column(db.DateTime(), doc="User identity confirmation datetime")
    roles = db.relationship(
        'Role',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    def __str__(self):
        return self.name

class Note(db.Model):
    """ User Notes """
    id = db.Column(db.String(32), primary_key=True, doc="Note id")
    note = db.Column(db.String(1024), doc="Note content")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))
    user = db.relationship('User', backref='notes')

    def __str__(self):
        return self.note

# Initialize the SQLAlchemy data store
user_datastore = SQLAlchemyUserDatastore(db, User, Role)

# Security is initialized in xAdmin

# Executes before the first request is processed.
@app.before_first_request
def before_first_request():

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles "admin" and "end-user" -- unless they already exist
    user_datastore.find_or_create_role(name=current_app.config['XADMIN_EDIT_ROLE'], description='Administrator (edit)')
    user_datastore.find_or_create_role(name=current_app.config['XADMIN_ROLE'], description='Administrator (view)')
    user_datastore.find_or_create_role(name='end-user', description='End user')

    # Create two Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    encrypted_password = utils.encrypt_password('password')
    if not user_datastore.get_user('someone@example.com'):
        user_datastore.create_user(email='someone@example.com', password=encrypted_password, name='User')
    if not user_datastore.get_user('vadmin@example.com'):
        user_datastore.create_user(email='vadmin@example.com', password=encrypted_password, name='Administrator (view only)')
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', password=encrypted_password, name='Administrator (edit)')

    # Commit any database changes; the User and Roles must exist before we can add a Role to the User
    db.session.commit()

    # Give one User has the "end-user" role, while the other has the "admin" role. (This will have no effect if the
    # Users already have these Roles.) Again, commit any database changes.
    user_datastore.add_role_to_user('someone@example.com', 'end-user')
    x=current_app
    user_datastore.add_role_to_user('vadmin@example.com', current_app.config['XADMIN_ROLE'])
    user_datastore.add_role_to_user('admin@example.com', current_app.config['XADMIN_ROLE'])
    user_datastore.add_role_to_user('admin@example.com', current_app.config['XADMIN_EDIT_ROLE'])

    note = Note(id='note4admin', user=user_datastore.get_user('admin@example.com'), note='Admin\'s note')
    db.session.add(note)

    note = Note(id='note4someone', user=user_datastore.get_user('someone@example.com'), note='Someone note')
    db.session.add(note)

    db.session.commit()


# Here comes example of Flask-xAdmin ModelViews

app.register_blueprint(xadm_app)

class myModelView(xModelView):
    column_exclude_list = 'password'
    # Customize your generic model -view
    pass

class myFileAdmin(xFileAdmin):
    def doc(self):
        return "Various files"

    # Customize your File Admin model -view
    pass


# IMPORTANT: Authorized users should have granted flask-xadmin role (for view only) flask-xadmin-edit (for edit feature)

# Prepare view list
views = [
    myModelView(model=User, session=db.session, category='Entities'),
    myModelView(model=Role, session=db.session, category='Entities'),
    myModelView(model=Note, session=db.session, category='Entities'),
    myFileAdmin(base_path='.', name="Files", category='Files')]

# Make an instance of flask-xadmin
xadmin_obj = gen_xadmin(app = app, title = 'xAdmin', db=db, user_model=User, role_model=Role, views=views)

@app.route('/')
def home():
    return redirect('/xadmin')

if __name__ == "__main__":
    app.run(debug=True, port=8001)
    print('Try url: /xadmin')

