from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission

def permission_required(permission):
    def decorator(f): #f表示为装饰的函数
        @wraps(f) #保留装饰器装饰的原函数的属性
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):              #在匿名的情况下，current_user是AnonymousUser的实例对象
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMIN)(f)
