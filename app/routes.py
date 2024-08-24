from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User
import sqlalchemy as sa


@app.route('/', methods=['GET', 'POST'])
def login_():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        flash("welcome to LaptopGuard")
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    logout_user()
    return
