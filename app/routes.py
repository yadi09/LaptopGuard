from app import app, db
from flask import render_template, flash, redirect, url_for, request, jsonify
from app.forms import LoginForm, RegistrationForm, SearchForm, UpdateStudentForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Student, Laptop, LibLogs, ExitLogs, LaptopImage
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


@app.route('/search_student')
def search_student():
    q = request.args.get("q")

    if q:
        all_student = Student.query.filter(Student.fullname.icontains(q) | Student.student_id.icontains(q) | Student.year.icontains(q) | Student.department.icontains(q) | Student.gender.icontains(q))
    else:
        all_student = []

    return render_template('all_student_list.html', all_student=all_student)


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
    students = Student.query.all()
    return students


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



@app.route('/delete_selected_students', methods=['POST'])
def delete_selected_students():
    try:
        data = request.get_json()
        selected_students = data.get('selected_students', [])
        if not selected_students:
            return jsonify(success=False,
                           message="No students selected"), 400
        
        delete_student_files(selected_students)

        """
        ExitLogs.query.filter(ExitLogs.student_id.in_(
            selected_students)).delete(synchronize_session=False)
        LibLogs.query.filter(LibLogs.student_id.in_(
            selected_students)).delete(synchronize_session=False)

        for std in selected_students:
            student = Student.query.filter(
                Student.student_id == std).first()
            laptop = Laptop.query.filter(
                Laptop.id == student.laptop_id).first()
            laptop_img = LaptopImage.query.filter(
                LaptopImage.laptop_in_id == laptop.id).all()

            "delete profile img and dir, std dir"
            if os.path.exists(student.profile_img):
                os.remove(student.profile_img)

            profile_img_dir_path = os.path.dirname(student.profile_img)
            std_dir = os.path.dirname(profile_img_dir_path)

            "delete laptop img and dir"
            for lp_img in laptop_img:
                if os.path.exists(lp_img.image_path):
                    os.remove(lp_img.image_path)

            dir_path = os.path.dirname(laptop_img[0].image_path)
            if os.path.exists(dir_path):
                try:
                    os.rmdir(dir_path)
                except Exception:
                    pass

            "delete profile_img dir and student dir"
            if os.path.exists(profile_img_dir_path):
                try:
                    os.rmdir(profile_img_dir_path)
                    os.rmdir(std_dir)
                except Exception:
                    pass

            "delete proccess"
            LaptopImage.query.filter(
                LaptopImage.laptop_in_id == laptop.id).delete(
                    synchronize_session=False)

            Student.query.filter(
                Student.student_id == student.student_id).delete(
                    synchronize_session=False)

            Laptop.query.filter(Laptop.id == laptop.id).delete(
                synchronize_session=False)

            db.session.commit()
"""
        return jsonify(
            success=True,
            message=f"Deleted {len(selected_students)} students.")

    except Exception as e:
        return jsonify(
            success=False,
            message="An error occurred while deleting students.",
            error=str(e)), 500



def delete_student_files(selected_students):
    ExitLogs.query.filter(ExitLogs.student_id.in_(
        selected_students)).delete(synchronize_session=False)
    LibLogs.query.filter(LibLogs.student_id.in_(
        selected_students)).delete(synchronize_session=False)
    
    for std in selected_students:
        student = Student.query.filter(
            Student.student_id == std).first()
        laptop = Laptop.query.filter(
            Laptop.id == student.laptop_id).first()
        laptop_img = LaptopImage.query.filter(
            LaptopImage.laptop_in_id == laptop.id).all()

        "delete profile img and dir, std dir"
        if os.path.exists(student.profile_img):
            os.remove(student.profile_img)

        profile_img_dir_path = os.path.dirname(student.profile_img)
        std_dir = os.path.dirname(profile_img_dir_path)

        "delete laptop img and dir"
        for lp_img in laptop_img:
            if os.path.exists(lp_img.image_path):
                os.remove(lp_img.image_path)

        dir_path = os.path.dirname(laptop_img[0].image_path)
        if os.path.exists(dir_path):
            try:
                os.rmdir(dir_path)
            except Exception:
                pass

        "delete profile_img dir and student dir"
        if os.path.exists(profile_img_dir_path):
            try:
                os.rmdir(profile_img_dir_path)
                os.rmdir(std_dir)
            except Exception:
                pass

        "delete proccess"
        LaptopImage.query.filter(
            LaptopImage.laptop_in_id == laptop.id).delete(
                synchronize_session=False)
        
        Student.query.filter(
            Student.student_id == student.student_id).delete(
                synchronize_session=False)
        
        Laptop.query.filter(Laptop.id == laptop.id).delete(
            synchronize_session=False)

        db.session.commit()
            
    
    


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
    student = db.session.scalar(sa.select(Student).where(Student.student_id == student_id))
    form = UpdateStudentForm(obj=student)

    if form.validate_on_submit():
        student.fullname = form.fullname.data
        student.student_id = form.studentId.data
        student.gender = form.gender.data
        student.year = form.year.data
        student.department = form.department.data

        if request.files['profile_img'].filename:
            if student.profile_img:
                try:
                    os.remove(student.profile_img)
                except Exception:
                    pass
            profile_img_path = os.path.dirname(student.profile_img)
            profile_img = request.files['profile_img']
            profile_img_filename = profile_img.filename
            profile_img_file_path = os.path.join(
                profile_img_path, profile_img_filename)
            profile_img.save(profile_img_file_path)
            student.profile_img = profile_img_file_path

        for i in range(1, 4):
            file_field = getattr(form, f'laptop_img{i}')
            if file_field.data:
                existing_img = student.laptop.images[i - 1].image_path
                if existing_img:
                    try:
                        os.remove(existing_img)
                    except Exception:
                        pass
                laptop_img_dirpath = os.path.dirname(existing_img)
                laptop_img = request.files[f'laptop_img{i}']
                laptop_img_filename = laptop_img.filename
                laptop_img_filepath = os.path.join(
                    laptop_img_dirpath, laptop_img_filename)
                laptop_img.save(laptop_img_filepath)
                student.laptop.images[i - 1].image_path = laptop_img_filepath
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for(
            'update_student', student_id=student.student_id))

    return render_template('update_student.html',
                           form=form, student=student)



@app.route('/student_profile_page/<studentId>')
@login_required
def student_profile(studentId):
    student = Student.query.filter(Student.student_id == studentId).first()
    return render_template('student_profile.html', student=student)



@app.route('/delete_student/<studentId>', methods=['POST'])
def delete_student(studentId):
    student = Student.query.filter(Student.student_id == studentId).first()
    if not student:
        return jsonify(success=False)

    delete_student_files([studentId])
    return jsonify(success=True)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))
