# -*- coding: utf-8 -*-
"""
权限验证
"""
from functools import wraps

from flask import  flash, url_for, redirect, abort
from flask_login import current_user

def permission_required(permission_name):
    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission_name):
                abort(403)
            return func(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(func):
    return permission_required('ADMINISTER')(func)
