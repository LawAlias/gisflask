from flask import flash,render_template
from module2 import app
@app.route('/module2',methods=['GET','POST'])
def module2():
    return ('module2 load success')