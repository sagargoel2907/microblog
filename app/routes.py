from app import app, db
from flask import render_template, flash, redirect, url_for, request, g
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EmptyForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post
import sqlalchemy as sa
from flask_login import login_user, current_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.email import send_password_reset_email
from flask_babel import _, get_locale

@app.before_request
def before_request():
    g.locale = str(get_locale())

@app.before_request
def add_last_seen():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Post added successfully'))
        return redirect(url_for('index'))

    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(current_user.following_posts(
    ), page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('index.html', posts=pagination.items, title='Home', form=form, pagination=pagination)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Post).where(
        Post.author != current_user).order_by(Post.timestamp.desc())
    pagination = db.paginate(
        query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    return render_template('index.html', posts=pagination.items, title='Explore', pagination=pagination)

@app.route('/login', methods=['GET', 'POST'])
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(
            form.username.data == User.username))
        if user is None or not user.check_password(form.password.data):
            flash(_('Incorrect username or password'))
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
        user = User(username=form.username.data,
                    email=form.email.data, about_me=form.about_me.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(_('Registered successfully!'))
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account_view():
    if request.method == 'POST':
        username = current_user.username
        db.session.delete(current_user)
        db.session.commit()
        logout_user()
        flash(_('Successfully deleted account of %(username)s', username=username))
        return redirect(url_for('login_view'))
    return render_template('confirm_account_delete.html')


@app.route('/profile/')
@app.route('/profile/<username>')
@login_required
def user_profile_view(username=None):
    if username:
        user = db.first_or_404(
            sa.select(User).where(User.username == username))
    else:
        user = current_user

    page = request.args.get('page', 1, type=int)
    # simply quering the db with select and where clause
    # query = sa.select(Post).where(
    #     Post.author == user).order_by(Post.timestamp.desc())

    # another way, getting posts from User.posts relationship and ordering in descending order
    query = user.posts.select().order_by(Post.timestamp.desc())
    posts = db.paginate(
        query, page=page, per_page=app.config['POSTS_PER_PAGE'])
    prev_url = url_for('user_profile_view', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    next_url = url_for('user_profile_view', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts, form=form, prev_url=prev_url, next_url=next_url)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile_view():
    form = EditProfileForm(current_user.username)
    if form.is_submitted() and form.validate():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Profile updated successfully'))
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', form=form)


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found', username=username))
            return redirect(url_for('index'))
        elif user == current_user:
            flash('You cannot follow yourself')
            return redirect(url_for('user_profile_view', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('User %(username)s followed successfully', username=username))
        return redirect(url_for('user_profile_view', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found', username=username))
            return redirect(url_for('index'))
        elif user == current_user:
            flash(_('You cannot unfollow yourself'))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('User %(username)s unfollowed successfully', username=username))
        return redirect(url_for('user_profile_view', username=username))
    else:
        return redirect(url_for('index'))


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user:
            send_password_reset_email(user)
        flash(_('Password reset link sent successfully'))
        return redirect(url_for('login_view'))
    return render_template('reset_password_request.html', form=form, title='Request Reset Password')


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password(token=token)
    if not user:
        flash(_('Invalid or expired token'))
        return redirect(url_for('login_view'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Password reset successful'))
        return redirect(url_for('login_view'))
    return render_template('reset_password.html', form=form, title='Reset Password')
