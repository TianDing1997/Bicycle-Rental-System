from flask import render_template, session, redirect, url_for, current_app, abort, flash, request
from .. import db
from ..models import Bike
from . import manage
from .forms import AddBike, DeleteBike, ChangeBike, SearchBike
from ..decorators import admin_required
from flask_uploads import UploadSet,IMAGES
from datetime import datetime
photos = UploadSet('photos',IMAGES)

@manage.route('/home')
def home():
    return render_template('manage/home.html')

@manage.route('/management')
@admin_required
def management():
    return render_template('manage/management.html')

@manage.route('/add_bike', methods=['GET', 'POST'])
def add_bike():
    bike = Bike()
    form = AddBike()
    if form.validate_on_submit():
        bike.type = form.type.data
        bike.brand = form.brand.data
        bike.rent_price = form.rent_price.data
        bike.number = form.number.data
        photo = request.files['photo']
        bike.image = "/upload/"+photo.filename
        if photo:
            photos.save(photo)
            flash('文件上传成功')
        db.session.add(bike)
        db.session.commit()
    return render_template('manage/add_bike.html',form=form)

@manage.route('/bike_info', methods=['GET', 'POST'])
def bike_info():
    bike = Bike.query.all()
    return render_template('manage/bike_info.html', bike=bike)

@manage.route('/delete_bike', methods=['GET', 'POST'])
def delete_bike():
    form = DeleteBike()
    if form.validate_on_submit():
        bike = Bike.query.filter_by(id=form.number.data).first_or_404()
        db.session.delete(bike)
        db.session.commit()
        if Bike.query.filter_by(id=form.number.data).first():
            flash('删除失败')
        else:
            flash('删除成功')
    return render_template('manage/delete_bike.html', form=form)

@manage.route('/change_bike', methods=['GET', 'POST'])
def change_bike():
    form = ChangeBike()
    bike = Bike()
    bike1 = Bike()
    if form.validate_on_submit():
        bike = Bike.query.filter_by(id=form.number.data).first_or_404()
        db.session.delete(bike)
        bike1.id = form.number.data
        bike1.type = form.type.data
        bike1.brand = form.brand.data
        bike1.rent_price = form.rent_price.data
        bike1.rent_price = form.rent_price.data
        bike1.image = request.files['photo'].read()
        photo = form.photo.data
        photos.save(photo)
        db.session.add(bike1)
        db.session.commit()
        if Bike.query.filter_by(id=form.number.data).first():
            flash('更改成功')
        else:
            flash('更改失败')
    return render_template('manage/change_bike.html', form=form)

@manage.route('/search_bike', methods=['GET', 'POST'])
def search_bike():
    form = SearchBike()
    if form.validate_on_submit():
        if form.key_type.data == '车型':
            bike = Bike.query.filter_by(type=form.key_word.data).all()
        elif form.key_type.data == '品牌':
            bike = Bike.query.filter_by(brand=form.key_word.data).all()
        elif form.key_type.data == '租金':
            bike = Bike.query.filter_by(rent_price=form.key_word.data).all()
        return render_template('manage/search_bike.html', form=form, bike=bike)
    else:
        return render_template('manage/search_bike.html', form=form)

@manage.route('/static', methods=['GET', 'POST'])
def static():
    bike = Bike().query.order_by(-Bike.rented_time).all()
    return render_template('manage/static.html', bike=bike)
