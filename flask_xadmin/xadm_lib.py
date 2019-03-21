# -*- coding: utf-8 -*-
# __author__ = 'dsedad'

from uuid import uuid4

import inspect

from flask_xadmin.xadm_salib import *
from flask import flash, current_app
from flask import redirect
from flask import request
from flask import url_for
from flask import session
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_redirect_target
from flask_admin.form import FormOpts
from flask_admin.model.base import get_mdict_item_or_list
from flask_security import current_user, logout_user
from flask_admin import Admin, expose, AdminIndexView, BaseView
from sqlalchemy.ext.declarative import AbstractConcreteBase
from flask_admin.contrib.fileadmin import FileAdmin
from flask_xadmin.forms import EditModeForm
from flask_security.utils import get_url
from flask_security.utils import encrypt_password
from wtforms import PasswordField

#from config import XADMIN_ROLE, XADMIN_EDIT_ROLE

LIST_TEMPLATE = 'admin/models/custom_list.html'
FILE_LIST_TEMPLATE = 'admin/files/custom_file_list.html'
DETAILS_TEMPLATE = 'admin/models/custom_details.html'
EDIT_TEMPLATE = 'admin/models/custom_edit.html'
CREATE_TEMPLATE = 'admin/models/custom_create.html'

PAGE_SIZE = 10

from flask_admin.contrib.sqla.form import AdminModelConverter
from flask_admin.model.form import converts
from wtforms import PasswordField
from wtforms import widgets

def xadmin_role():
    role = current_app.config.get('XADMIN_ROLE')
    if role == None:
        role = 'flask-xadmin'
        current_app.config['XADMIN_ROLE'] = role
    return role


def xadmin_edit_role():
    role = current_app.config.get('XADMIN_EDIT_ROLE')
    if role == None:
        role = 'flask-xadmin-edit'
        current_app.config['XADMIN_EDIT_ROLE'] = role
    return role


def is_user_authenticated():
    """
    Wrapper for user.is_authenticated
    :return:
    """
    try:
        result = current_user.is_authenticated()
    except:
        result = current_user.is_authenticated
    return result


def is_super_admin():
    return current_user.has_role(xadmin_role())

def is_super_admin_edit():
    return current_user.has_role(xadmin_edit_role())

class CustomPasswordInput(widgets.Input):
    input_type = 'password'

    def __init__(self, hide_value=True):
        self.hide_value = hide_value

    def __call__(self, field, **kwargs):
        return super(CustomPasswordInput, self).__call__(field, **kwargs)

class CustomPasswordField(PasswordField):
    #custom password filed, does not hide value
    widget = CustomPasswordInput()

class PasswordAdminModelConverter(AdminModelConverter):
    #custom model converter for converting Password column types to custom password filed form field
    @converts('Password')
    def conv_Password(self, field_args, **extra):
        field_args.setdefault('label', u'Password')
        return CustomPasswordField(**field_args)


def current_edit_mode():
    return session.get('xadm_edit_mode', False)

def set_edit_mode(mode):
    if mode:
        if is_super_admin_edit():
            session['xadm_edit_mode'] = True
        else:
            raise Exception(u'Not allowed')
    else:
        edit_mode = session.get('xadm_edit_mode', None)
        if edit_mode != None:
            session.pop('xadm_edit_mode')

class BaseClass(AbstractConcreteBase):
    # table page size
    page_size = PAGE_SIZE
    details_modal = False

    def is_accessible(self):
        if is_user_authenticated():
            return is_super_admin()

    # if view is not accessible redirect to login page
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))

    list_template = LIST_TEMPLATE
    details_template = DETAILS_TEMPLATE
    edit_template = EDIT_TEMPLATE
    create_template = CREATE_TEMPLATE

class xModelView(BaseClass, ModelView):
    column_display_pk = True
    read_only = False
    encrypt_password_fields = True
    _password_type_name = 'password'


    def on_model_change(self, form, model_obj, is_created):
        if self.encrypt_password_fields:
            model = inspect_sa(model_obj).mapper.class_ #we need model not model object
            keys = sa_type_keys(model, self._password_type_name) #column type is in lowercase
            for k in keys:
                password_changed = sa_column_changed(model_obj, k)
                if password_changed:
                    password_field = getattr(form, k)
                    print(encrypt_password(password_field.data))
                    setattr(model_obj, k, encrypt_password(password_field.data))

    def set_permissions(self, edit_mode):
        """
        edit_mode == True => allow edit, delete, create. Otherwise prevent edit, delete, create.
        :return:
        """
        if not is_super_admin_edit():
            edit_mode = False

        if not(edit_mode):
            self.can_create = False
            self.can_edit = False
            self.can_delete = False
            self.can_view_details = True
        else:
            if (hasattr(self, 'read_only') and self.read_only):
                self.can_create = False
                self.can_edit = False
                self.can_delete = False
                self.can_view_details = True
            else:
                self.can_create = True
                self.can_edit = True
                self.can_delete = True
                self.can_view_details = True
                    # return dict(edit_mode=True)
    def doc(self):
        if(inspect.getdoc(self.model)):
            return inspect.getdoc(self.model).strip()#金铭改
        else:
            return ''

    @expose('/details/', methods=('GET', 'POST'))
    def details_view(self):

        return_url = get_redirect_target() or self.get_url('.index_view')
        id = get_mdict_item_or_list(request.args, 'id')
        if id is None:
            return redirect(return_url)
        model = self.get_one(id)
        if model is None:
            return redirect(return_url)
        form = self.edit_form(obj=model)
        form_opts = FormOpts(widget_args=self.form_widget_args,
                             form_rules=self._form_edit_rules)

        self.on_form_prefill(form, id)

        return self.render(self.details_template,
                           model=model,
                           form=form,
                           form_opts=form_opts,
                           return_url=return_url)

    def scaffold_list_filters(self):
        cols = self.scaffold_list_columns()
        # Columns
        res_cols = []
        # Relationships
        res_rels = []
        for c in cols:
            col_type = sa_column_type(self.model, c)
            if col_type is None:
                res_rels.append(c)
            elif sa_column_type(self.model, c) not in ('password', 'guid', 'largebinary'): #If we use custom filed filter will not work
                res_cols.append(c)
        # Filter show list of columns, then list of relationships
        return res_cols + res_rels

    def get_form_columns(self, directions=[MANYTOMANY, ONETOMANY]):
        return self.scaffold_list_columns() + sa_relationships_keys(self.model, directions=directions)

    def get_column_searchable_list(self):
        return sa_column_searchable_list(self.model)

    def get_column_list(self):
        return self.scaffold_list_columns()

    def get_column_list_filters(self):
        return self.scaffold_list_filters()

    def get_column_descriptions(self):
        return sa_column_descriptions(self.model)

    def get_column_formatters(self):
        return gen_href_formatter(self.model)

    def get_column_details_list(self):
        return self.get_form_columns(directions=[MANYTOMANY, ONETOMANY])

    def __init__(self, *args, **kwargs):
        # if not(self.column_formatters):
        #    self.column_formatters = gen_href_formatter(model, relationship_names=['log_create_user'])
        self.model = kwargs.get('model')
        if not self.model:
            self.model = args[0]

        ahref_fmt = '<a href="#" data-toggle="modal" title="View Record" data-target="#fa_modal_window" data-remote="%s&modal=True">%s</a>'
        if not getattr(self, "column_formatters"):
            formatters = dict(self.get_column_formatters())
            self.column_formatters = formatters

        if not getattr(self, "column_descriptions"):
            self.column_descriptions = self.get_column_descriptions()

        if not getattr(self, "column_filters"):
            self.column_filters = self.get_column_list_filters()
            pass

        if not getattr(self, "column_list"):
            self.column_list = self.get_column_list()

        if not getattr(self, "column_searchable_list"):
            self.column_searchable_list = self.get_column_searchable_list()

        if not getattr(self, "form_columns"):
            self.form_columns = self.get_form_columns(directions=[MANYTOMANY, ONETOMANY])

        if not getattr(self, "column_details_list"):
            self.column_details_list = self.get_column_details_list()

        if self.encrypt_password_fields:
            self.model_form_converter = PasswordAdminModelConverter

        super(xModelView, self).__init__(*args, **kwargs)



class xAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        return super(xAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        set_edit_mode(False)
        logout_user()
        return redirect(url_for('.index'))


class xEditModeView(BaseView):
    def is_accessible(self):
        if is_user_authenticated():
            return is_super_admin()
        return False

    def is_visible(self):
        return False

    # if view is not accessible redirect to login page
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))

    #enter edit mode function
    @expose('/', methods=('GET', 'POST'))
    def change_mode(self):
        form = EditModeForm()
        if form.validate_on_submit():
            set_edit_mode(True)
            flash(u'You are in EDIT mode. Be wise and careful!')
            return redirect(form.next.data)
        form.next.data = get_url(request.args.get('next')) or '/'
        return self.render('admin/edit_mode.html', edit_mode_form=form)

        # from flask_security.utils import verify_and_update_password
        #if request.method == 'GET':
        #    return self.render('admin/edit_mode.html',edit_mode_form=form)
        #else:
        #   password = request.form['password']
        #  # previous_page = request.form['previous_page']
        #   if verify_and_update_password(password, current_user):
        #       session['xadm_edit_mode'] = True
        #       flash(u'You are in EDIT mode. Be wise and careful!')
        #       return redirect('/')
        #       #return self.render('index.html')
        #   else:
        #      flash(u'Wrong password', category='error')
        #      return self.render('admin/edit_mode.html',edit_mode_form=form)

    # exit edit mode function
    @expose('/leave_edit', methods=['GET'])
    def leave_edit(self):
        try:
            set_edit_mode(False)
        except:
            pass
        flash(u"You've left EDIT mode.")
        return redirect(request.referrer or '/')

# Custom base file admin class
class xFileAdmin(FileAdmin):
    list_template = FILE_LIST_TEMPLATE
    read_only = False
    def doc(self):
        return ""

    def is_accessible(self):
        if is_user_authenticated():
            return is_super_admin()
        return False

    # if view is not accessible redirect to login page
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))

    def set_permissions(self, edit_mode):
        """
        edit_mode == True => allow edit, delete, create. Otherwise prevent edit, delete, create.
        :return:
        """
        if not (edit_mode):
            self.can_download = True
            self.can_mkdir = False
            self.can_delete_dirs = False
            self.can_delete = False
            self.can_rename = False
            self.can_upload = False
        else:
            if (hasattr(self, 'read_only') and self.read_only):
                self.can_download = True
                self.can_mkdir = False
                self.can_delete_dirs = False
                self.can_delete = False
                self.can_rename = False
                self.can_upload = False
            else:
                self.can_download = True
                self.can_mkdir = True
                self.can_delete_dirs = True
                self.can_delete = True
                self.can_rename = True
                self.can_upload = True
                # return dict(edit_mode=True)
