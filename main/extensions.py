from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_moment import Moment
from flask_dropzone import Dropzone
from flask_whooshee import Whooshee
toolbar=DebugToolbarExtension()
bootstrap=Bootstrap()
db=SQLAlchemy()
whooshee=Whooshee()
login_manager = LoginManager()
moment = Moment()
dropzone=Dropzone()
@login_manager.user_loader
def load_user(user_id):
    from main.models import User
    user = User.query.get(int(user_id))
    return user


login_manager.login_view = 'login'
# login_manager.login_message = 'Your custom message'
login_manager.login_message_category = 'warning'