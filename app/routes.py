from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from app.models import User, Post
import sqlalchemy as sa
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone


@app.before_request
def add_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': 'abc',
            'content': 'lorem ipsum text',
        },
        {
            'author': 'abc',
            'content': 'lorem ipsum text',
        },
    ]
    user = {'username:': 'falana'}
    posts = db.session.scalars(sa.select(Post))
    return render_template('index.html', posts=posts, title='Home', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(
            form.username.data == User.username))
        if user is None or not user.check_password(form.password.data):
            flash('Incorrect username or password')
            return redirect(url_for('login_view'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form=form)


@app.route('/logout')
def logout_view():
    logout_user()
    return redirect(url_for('login_view'))


@app.route('/register', methods=['GET', 'POST'])
def register_view():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, about_me=form.about_me.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registered successfully!")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account_view():
    print(request.method)
    if request.method == 'POST':
        username = current_user.username
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash(f'Successfully deleted account of {username}')
        return redirect(url_for('login_view'))
    return render_template('confirm_account_delete.html')


@app.route('/profile/')
@app.route('/profile/<username>')
@login_required
def user_profile_view(username=None):
    if username:
        user = db.first_or_404(sa.select(User).where(User.username == username))
    else:
        user = current_user
    posts = [
        {
            'author': 'abc',
            'content': 'lorem ipsum text',
        },
        {
            'author': 'abc',
            'content': 'lorem ipsum text',
        },
    ]
    posts = db.session.scalars(sa.select(Post).where(Post.author == user))
    return render_template('user.html', user=user, posts=posts)

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile_view():
    form = EditProfileForm(current_user.username)
    if form.is_submitted() and form.validate():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    
    return render_template('edit_profile.html', form=form)
