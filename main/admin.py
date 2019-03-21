# -*- coding: utf-8 -*-
"""
    管理员
"""
import os
import uuid
from flask import render_template, flash, redirect, url_for, request, current_app, Blueprint, send_from_directory
from flask_login import login_required, current_user

from main.extensions import db
from main.utils import redirect_back
from main import app
from werkzeug import secure_filename

@app.route('/file/new', methods=['GET', 'POST'])
@login_required
def new_file():
    if request.method == 'POST':
        f = request.files.get('file')
        f.save(os.path.join(app.config['UPLOADED_PATH'], f.filename))
    return render_template('admin/new_file.html')
