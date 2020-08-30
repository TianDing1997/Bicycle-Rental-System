#
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown
from datetime import timedelta
from flask_uploads import UploadSet, IMAGES, configure_uploads, patch_request_class

bootstrap = Bootstrap()#在此时还未传入参数，扩展并没有初始化
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
photos = UploadSet('photos',IMAGES)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'#p82 匿名用户尝试登陆的时候会返回登陆界面


def create_app(config_name):#工厂函数：把创建实例过程移到可显示调用的工厂函数
    app = Flask(__name__)#创建WSGI应用实例
    app.config.from_object(config[config_name])#将config.py中保存的配置导入应用
    config[config_name].init_app(app)
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
    #配置上传对象
    configure_uploads(app,photos)

    #设置上传文件大小，默认64M，设置为None时，大小由'MAX_CONTENT_LENGTH'决定
    patch_request_class(app)

    bootstrap.init_app(app)#初始化
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    from .main import main as main_blueprint#注册蓝本
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')#url_prefix蓝本中定义的所有路由都会加上指定的前缀

    from .manage import manage as manage_blueprint
    app.register_blueprint(manage_blueprint, url_prefix='/manage')

    return app#工厂返回创建的应用实例
