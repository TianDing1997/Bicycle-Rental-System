from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin #UserMixin类，提供默认实现， p82
from . import login_manager, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer #T.....Serializer生成具有过期时间的JSON Web签名，接受密钥为参数
from flask import current_app
from datetime import datetime
from markdown import markdown
import bleach

class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16

#角色表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod#静态对象不需要实例化，也不用返回值, 也不需要self
    def insert_roles():
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN],


        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            #print("role1=",role)
            if role is None:
                role = Role(name=r)#先定义角色
            role.reset_permissions()#重置角色权限
            #print("role2=",role)
            for perm in roles[r]:#将对应角色的权限一个一个赋给角色
                role.add_permission(perm)
                #print("role3=", role)
            role.default = (role.name == default_role)
            #print("role.default=", role.default)
            db.session.add(role)
        db.session.commit()



    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)#对继承自父类的属性初始化
        if self.permissions is None:
            self.permissions=0

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm#按位与运算符：参与运算的两个值,如果两个相应位都为1,则该位的结果为1,否则为0

    def __repr__(self):
        return '<Role %r>' % self.name
#租车表
class Rent(db.Model):
    __tablename__ = 'rents'
    rent_id = db.Column(db.Integer, primary_key=True)
    renter_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    rented_bike_id = db.Column(db.Integer, db.ForeignKey('bikes.id'))
    rent_price = db.Column(db.Float)
    rent_time = db.Column(db.DateTime)
    return_time = db.Column(db.DateTime)

#用户表
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    rented_bike = db.relationship('Rent',
                                  foreign_keys=[Rent.renter_id],
                                  backref=db.backref('renter',lazy='joined'),
                                  lazy='dynamic',
                                  cascade='all, delete-orphan')
    #当对数据库模型做出更改后，如果使用迁移框架管理数据库，必须在迁移脚本中定义所有改动， 否则
    #改动不可复现。步骤p59: flask db migrate,#flask db upgrade

    #赋予角色：
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)#调用User的构造函数
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
    #检验角色：
    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    #邮件
    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'confirm': self.id}).decode('utf-8')#生成一个加密签名

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))#解码令牌
        except:
            return False
        if data.get('confirm') != self.id:#确保一个令牌有且只有一个用户对应
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    #s刷新用户最后访问时间
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()


    #不可读
    @property#get的功能,返回密码是不可读的
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter#set的功能，设置.password_hash为密码散列值
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean( #clean函数删除所有不在白名单中的标签，linkify将纯文本中的URL转换成<a>
            markdown(value, output_format='html'),#markdown函数把Markdown文本转换成HTML
            tags=allowed_tags, strip=True #把得到的结果和允许使用的HTML标签列表传个clean()函数。
        ))

db.event.listen(Post.body, 'set', Post.on_changed_body)#on_changed_body()是SQLAlchemy“set”事件的监听程序，只要body字段更新了新值，函数就会被动调用

class Bike(db.Model):
    __tablename__ = 'bikes'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(64), index=True)
    brand = db.Column(db.String(64), index=True)
    rent_price = db.Column(db.Integer)
    number = db.Column(db.Integer)
    image = db.Column(db.Text)
    rented_time = db.Column(db.Integer, default=0)
    total_charge = db.Column(db.Float,default=0)
    renter = db.relationship('Rent',
                            foreign_keys=[Rent.rented_bike_id],
                            backref=db.backref('rented',lazy='joined'),
                            lazy='dynamic',
                            cascade='all, delete-orphan')



class AnonymousUser(AnonymousUserMixin): #P101
    def can(self, permission):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser#告诉Flask_Login使用应用自定义的匿名用户类

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
