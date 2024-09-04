from app import app, db
from flask import render_template, flash, redirect, url_for, request, jsonify
from app.forms import LoginForm, RegistrationForm, SearchForm, UpdateStudentForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Student, Laptop, LibLogs, ExitLogs
from datetime import datetime
import sqlalchemy as sa
import sqlalchemy.orm as so
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
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
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
        checked_in_students = get_checked_in_students()
        form = SearchForm()
        if form.validate_on_submit():
            student_id = form.student_id.data
            student = Student.query.filter_by(
                student_id=student_id).first()
            if not student:
                flash('Student not found', 'nfound')
            return render_template(
                'lib.html',
                form=form,
                student=student,
                checked_in_students=checked_in_students)
        return render_template(
            'lib.html',
            form=form,
            student=None,
            checked_in_students=checked_in_students)
    else:
        logout_user()
        return redirect(url_for('login'))


@app.route('/exit_check_in', methods=['GET', 'POST'])
@login_required
def exit():
    if current_user.username == 'exit':
        checked_out_students = get_checked_out_students()
        form = SearchForm()
        if form.validate_on_submit():
            student_id = form.student_id.data
            student = Student.query.filter_by(
                student_id=student_id).first()
            if not student:
                flash('Student not found', 'nfound')
            return render_template('exit.html',
                                   form=form,
                                   student=student,
                                   checked_out_students=checked_out_students)
        return render_template('exit.html',
                               form=form,
                               student=None,
                               checked_out_students=checked_out_students)
    else:
        logout_user()
        return redirect(url_for('login'))


@app.route('/admin_dashboard', methods=['GET', 'POST'])
@login_required
def admin():
    all_student = get_all_students()
    form = RegistrationForm()
    if current_user.username == 'admin':
        flash("welcome to LaptopGuard")
        return render_template(
            'all_student.html', form=form, all_student=all_student)
    else:
        logout()
        return redirect(url_for('login'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        student_id = form.student_id.data
        student = Student.query.filter_by(student_id=student_id).first()
        if not student:
            flash('Student not found', 'nfound')
    return redirect('lib.html', form=form, student=student)



def get_checked_in_students():
    latest_log_alias = so.aliased(LibLogs)

    subquery = (
        sa.select(
            latest_log_alias.student_id,
            sa.func.max(latest_log_alias.timestamp).label('max_id')
        )
        .group_by(latest_log_alias.student_id)
        .subquery()
    )

    query = (
        sa.select(Student)
        .join(subquery, Student.student_id == subquery.c.student_id)
        .join(LibLogs, LibLogs.timestamp == subquery.c.max_id)
        .where(LibLogs.status == 'IN')
    )

    checked_in_students = db.session.scalars(query).all()

    return checked_in_students


def get_checked_out_students():
    latest_log_alias = so.aliased(ExitLogs)

    subquery = (
        sa.select(
            latest_log_alias.student_id,
            sa.func.max(latest_log_alias.timestamp).label('max_id')
        )
        .group_by(latest_log_alias.student_id)
        .subquery()
    )

    query = (
        sa.select(Student)
        .join(subquery, Student.student_id == subquery.c.student_id)
        .join(ExitLogs, ExitLogs.timestamp == subquery.c.max_id)
        .where(ExitLogs.status == 'OUT')
    )

    checked_out_students = db.session.scalars(query).all()

    return checked_out_students


def get_all_students():
    query = sa.select(Student)
    students = db.session.execute(query).all()
    list_of_students = []
    for std in students:
        list_of_students.append(std[0])
    return list_of_students


@app.route('/update_lib_status/<student_id>', methods=['GET', 'POST'])
def update_lib_status(student_id):
    student = db.session.scalar(
        sa.select(Student).where(Student.student_id == student_id))

    if student is None:
            return jsonify({'error': 'Student not found'}), 404

    if not student.lib_logs:
        new_log = LibLogs(student_id=student.student_id, status='IN')
        db.session.add(new_log)
    else:
        last_log = student.lib_logs[-1]
        if last_log.status == 'OUT':
            new_log = LibLogs(student_id=student.student_id, status='IN')
            db.session.add(new_log)
        else:
            time_spent = datetime.utcnow() - last_log.timestamp
            student.total_library_time += time_spent

            new_log = LibLogs(student_id=student.student_id, status='OUT')
            db.session.add(new_log)

    db.session.commit()
    checked_in_students = get_checked_in_students()
    checked_in_students_html = render_template(
        'checked_in_students_list.html', checked_in_students=checked_in_students)
    return jsonify({'status': new_log.status,
                    'total_library_time': str(student.total_library_time),
                    'checked_in_students_html': checked_in_students_html})




@app.route('/update_exit_status/<student_id>', methods=['GET', 'POST'])
def update_exit_status(student_id):
    student = db.session.scalar(
        sa.select(Student).where(Student.student_id == student_id))

    if student is None:
        return jsonify({'error': 'Student not found'}), 404

    if not student.exit_logs:
        new_log = ExitLogs(student_id=student.student_id, status='OUT')
        db.session.add(new_log)
    else:
        last_log = student.exit_logs[-1]
        if last_log.status == 'OUT':
            new_log = ExitLogs(student_id=student.student_id, status='IN')
            db.session.add(new_log)
        else:
            new_log = ExitLogs(student_id=student.student_id, status='OUT')
            db.session.add(new_log)

    db.session.commit()
    checked_out_students = get_checked_out_students()
    checked_out_students_html = render_template(
        'checked_out_students_list.html', checked_out_students=checked_out_students)
    return jsonify({'status': new_log.status,
                    'checked_out_students_html': checked_out_students_html})



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

        
    db.session.add(student)
    db.session.add(laptop)
    db.session.commit()

    return True




@app.route('/update_student/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.get_or_404(student_id)
    form = UpdateStudentForm(obj=student)

    if form.validate_on_submit():
        student.fullname = form.fullname.data
        student.student_id = form.studentId.data
        student.gender = form.gender.data
        student.year = form.year.data
        student.department = form.department.data

        if form.profile_img.data:
            if student.profile_img:
                os.remove(student.profile_img)
            profile_img_path = os.path.dirname(student.profile_img)
            profile_img_filename = form.profile_img.data.filename
            profile_img_file_path = os.path.join(
                profile_img_path, profile_img_filename)
            form.profile_img.data.save(profile_img_file_path)
            student.profile_img = profile_img_file_path

        for i in range(1, 4):
            file_field = getattr(form, f'laptop_img{i}')
            if file_field.data:
                existing_img = student.laptop.images[i].image_path
                if existing_img:
                    os.remove(existing_img)
                laptop_img_dirpath = os.path.dirname(existing_img)
                laptop_img_filename = file_field.data.filename
                laptop_img_filepath = os.path.join(
                    laptop_img_dirpath, laptop_img_filename)
                file_field.data.save(laptop_img_filepath)
                student.laptop.images[i].image_path = laptop_img_filepath
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('admin_page'))
    
    return render_template('update_student.html', form=form, student=student)









@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
