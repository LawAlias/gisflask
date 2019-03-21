# -*- coding: utf-8 -*-
from flask_security.forms import Form,LoginForm
from wtforms import SubmitField, PasswordField,HiddenField
from flask_security.utils import verify_and_update_password
from flask_security import current_user
from werkzeug.security import check_password_hash

#Form to enter edit mode
class EditModeForm(Form):
    password = PasswordField(u'Password', description='Please enter your password to enable edit mode')
    next = HiddenField()
    submit = SubmitField(u'Activate edit mode')

    def validate(self):
        if not Form.validate(self):
            return False

        if self.password.data.strip() == '':
            self.password.errors.append(u'Password is required')
            return False
        print(self.password.data)
        if not check_password_hash(self.password.data, current_user.password):
            self.password.errors.append(u'Wrong password')
            return False

        return True

