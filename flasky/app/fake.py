from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post

def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(), #虚拟对象的属性使用Faker包提供的随即信息生成器生成
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date()
                 )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError: #如果生成了重复的电子邮件和用户名，提交数据库会话时会抛出此异常。
            db.session.rollback()

def posts(count=100):
    fake = Faker()
    user_count = User.query.count()
    for i in range(count):
        u = User.query.offset(randint(0, user_count - 1)).first()#查询是题
        p = Post(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u
        )
        db.session.add(p)
    db.session.commit()
