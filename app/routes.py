from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Student
import sqlalchemy as sa


@app.route('/', methods=['GET', 'POST'])
def login_():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.id == 2:
            return redirect(url_for('admin'))
        elif current_user.id == 3:
            return redirect(url_for('lib'))
        else:
            return redirect(url_for('exit'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        if user.username == "admin":
            return redirect(url_for('admin'))
        elif user.username == "lib":
            return redirect(url_for('lib'))
        else:
            return redirect(url_for('exit'))
    return render_template('login.html', form=form)


@app.route('/registration_form')
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        student = db.session.scalar(select(Student).where(Student.student_id == form.studentId.data))
        if not student:
            student = Student(student_id=form.studentId.data, fullname=form.fullname.data, gender=)


@app.route('/library_check_in')
@login_required
def lib():
    if current_user.username == 'lib':
        flash("welcome to LaptopGuard")
        return render_template('lib.html')
    else:
        logout_user()
        return redirect(url_for('login'))


@app.route('/exit_check_in')
@login_required
def exit():
    if current_user.username == 'exit':
        flash("welcome to LaptopGuard")
        return render_template('exit.html')
    else:
        logout_user()
        return redirect(url_for('login'))


@app.route('/admin_dashboard')
@login_required
def admin():
    if current_user.username == 'admin':
        flash("welcome to LaptopGuard")
        return render_template('all_student.html')
    else:
        logout()
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
