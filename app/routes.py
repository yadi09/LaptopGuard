from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, SearchForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Student, Laptop
import sqlalchemy as sa
import os


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


@app.route('/library_check_in', methods=['GET', 'POST'])
@login_required
def lib():
    if current_user.username == 'lib':
        form = SearchForm()
        student_id = form.student_id.data
        student = Student.query.filter_by(student_id=student_id).first()
        if form.validate_on_submit():
            if not student:
                flash('Student not found', 'nfound')
        return render_template('lib.html', form=form, student=student)
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


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin():
    form = RegistrationForm()
    if current_user.username == 'admin':
        flash("welcome to LaptopGuard")
        return render_template('all_student.html', form=form)
    else:
        logout()
        return redirect(url_for('login'))


@app.route('/register_student', methods=['POST'])
def register_student():
    form = RegistrationForm()
    show_sidebar = False

    if form.validate_on_submit():
        student = db.session.scalar(
            sa.select(Student).where(Student.student_id == form.studentId.data))
        if not student:
            student = Student(
                student_id=form.studentId.data,
                fullname=form.fullname.data,
                gender=form.gender.data,
                year=form.year.data,
                department=form.department.data
            )

            
            retn_val = upload_imgs(form, student)
            if not retn_val:
                show_sidebar = True
                return redirect(url_for('admin'))

            flash('Student registered successfully!', 'success')
            return redirect(url_for('admin'))
        else:
            form.studentId.errors.append("Student ID already exists")
            show_sidebar = True
    else:
        show_sidebar = True
    return render_template('all_student.html',
                               form=form,
                               show_sidebar=show_sidebar)


def upload_imgs(form, student):
    upload_folder = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
         os.makedirs(upload_folder)

    student_id = request.form['studentId']
    profile_img = request.files['profile_img']
    laptop_img1 = request.files['laptop_img1']
    laptop_img2 = request.files['laptop_img2']
    laptop_img3 = request.files['laptop_img3']


    student_folder = os.path.join(app.config['UPLOAD_FOLDER'], student_id)
    student_profile_folder = os.path.join(student_folder, 'profile_img')
    student_laptop_folder = os.path.join(student_folder, 'laptop_img')
    

    if not os.path.exists(student_profile_folder):
        os.makedirs(student_profile_folder)
    if not os.path.exists(student_laptop_folder):
        os.makedirs(student_laptop_folder)

    profile_img_path = os.path.join(
        student_profile_folder, profile_img.filename)
    profile_img.save(profile_img_path)
    student.profile_img = profile_img_path

    laptop = Laptop()
    laptop_img_path1 = os.path.join(
        student_laptop_folder, laptop_img1.filename)
    laptop.add_laptop_image(laptop_img_path1)
    laptop_img1.save(laptop_img_path1)

    laptop_img_path2 = os.path.join(
        student_laptop_folder, laptop_img2.filename)
    laptop.add_laptop_image(laptop_img_path2)
    laptop_img2.save(laptop_img_path2)

    laptop_img_path3 = os.path.join(
        student_laptop_folder, laptop_img3.filename)
    laptop.add_laptop_image(laptop_img_path3)
    laptop_img3.save(laptop_img_path3)
    laptop.student = student

    """laptop = Laptop()
    laptop.student = student"""

    """for i in range(3):
        laptop_img_path = os.path.join(
            student_laptop_folder, laptop_file[i])    
        laptop.add_laptop_image(laptop_img_path)
        file = request.files.get(f'laptop_img-{i}')
        file.save(laptop_img_path)"""
        
    db.session.add(student)
    db.session.add(laptop)
    db.session.commit()

    return True


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            flash('Student not found', 'nfound')
    return redirect('lib.html', form=form, student=student)





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
