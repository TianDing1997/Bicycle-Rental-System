from flask import render_template, session, redirect, url_for, current_app, abort, flash, request
from .. import db
from ..models import User, Role, Post, Permission, Bike, Rent
from ..email import send_email
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from flask_login import login_required, current_user
from ..decorators import admin_required
from datetime import datetime





@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object()

        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    #posts = Post.query.order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int) #120
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], #per_page显示每叶显示的数据量
        error_out=False
    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                            pagination=pagination)

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], #per_page显示每叶显示的数据量
        error_out=False
    )
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,pagination=pagination)

#资料编辑：
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)#因为id由URL的动态参数决定，所以可以用get_or_404()
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username =form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash(' The profile has been updated.')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form, user=user)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and\
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('The post has been updated')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)

@main.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    bike = Bike.query.all()
    return render_template('home.html', bike=bike)

@main.route('/current_bike_rent/<int:id>', methods=['GET', 'POST'])
@login_required
def bike_rent(id):
    bike = Bike.query.filter_by(id=id).first()
    rent = Rent()
    if bike.number >= 1:
        bike.number = bike.number-1
        bike.rented_time = bike.rented_time + 1
        rent.renter_id = current_user.id
        rent.rented_bike_id = bike.id
        rent.rent_time = datetime.utcnow()
        db.session.add(rent)
        db.session.add(bike)
        db.session.commit()
        return render_template('current_bike_rent.html', rent=[rent])
    else:
        flash('单车数量不足')
        return redirect(url_for('.home'))

@main.route('/bike_rent_info/<int:id>', methods=['GET', 'POST'])
@login_required
def bike_rent_info(id):
    rent = Rent.query.filter_by(renter_id=id).all()
    bike = Bike()
    return render_template('bike_rent_info.html', rent=rent, bike=bike)

@main.route('/bike_return/<int:id>', methods=['GET', 'POST'])
@login_required
def bike_return(id):
    rent = Rent.query.filter_by(rent_id=id).first()
    bike = Bike.query.filter_by(id=rent.rented_bike_id).first()
    if not rent.return_time:
        rent.return_time = datetime.utcnow()
        rent.rent_price = round((rent.return_time-rent.rent_time).total_seconds()*(1/3600),2)*bike.price
        bike.total_charge = bike.total_charge + rent.rent_price
        bike.number = bike.number+1
        db.session.add(rent)
        db.session.add(bike)
        db.session.commit()
        return render_template('bike_return.html', rent=rent, bike=bike)
    else:
        return render_template('bike_return.html', rent=rent, bike=bike)

@main.route('/bike_pay/<int:id>', methods=['GET', 'POST'])
@login_required
def bike_pay(id):
    rent = Rent.query.filter_by(rent_id=id).first()
    db.session.delete(rent)
    db.session.commit()
    flash('支付成功')
    return redirect(url_for('.bike_rent_info', id=current_user.id))
