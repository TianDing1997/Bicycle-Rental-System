#创建一个蓝本解决需要在调用create_app()之后才能使用装饰器的问题
#将视图方法模块化，既当大量的视图函数放在一个文件中，很明显是不合适，
#最好的方案是根据功能将路由合理的划分到不同的文件中；而蓝本就是为了解决这个问题而出现的。
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor#使变量在所有模版中可访问。
def inject_permissions():
    return dict(Permission=Permission)
