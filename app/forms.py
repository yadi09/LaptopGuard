from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=15)])
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=4, max=16)])
    remember_me = BooleanField('Remember Me')
    Login = SubmitField('Login')


class RegistrationForm(FlaskForm):
    fullname = StringField(
        'Full Name', validators=[DataRequired(), Length(min=1, max=20)])
    studentId = StringField(
        'Student ID',
        validators=[DataRequired(), Length(max=20)],
        render_kw={"placeholder": "25021"})

    gender = SelectField(
        'Gender',
        choices=[('', 'Choose'),('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        validators=[DataRequired()])
    year = SelectField(
        'Year',
        choices=[
            ('', 'Choose'),
            ('1', '1st Year'),
            ('2', '2nd Year'),
            ('3', '3rd Year'),
            ('4', '4th Year')],
        validators=[DataRequired()])
    department = SelectField(
        'Department', choices=[
            ('', 'Choose'),
            ('CS', 'Computer Science'),
            ('ENG', 'Engineering'),
            ('BIZ', 'Business'),
            ('ART', 'Arts')],
        validators=[DataRequired()])

    profile_img = FileField(
        'Profile Picture',
        validators=[DataRequired(), FileAllowed(
            ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
            'Images only!')])
    laptop_img1 = FileField(
        'Laptop Picture 1',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])
    laptop_img2 = FileField(
        'Laptop Picture 2',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])
    laptop_img3 = FileField(
        'Laptop Picture 3',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])

    submit = SubmitField('Register')



class SearchForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])
    submit = SubmitField('Search')



class UpdateStudentForm(FlaskForm):
    fullname = StringField(
        'Full Name', validators=[DataRequired(), Length(min=1, max=20)])
    studentId = StringField(
        'Student ID',
        validators=[DataRequired(), Length(max=20)])

    gender = SelectField(
        'Gender',
        choices=[('', 'Choose'),('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        validators=[DataRequired()])
    year = SelectField(
        'Year',
        choices=[
            ('', 'Choose'),
            ('1', '1st Year'),
            ('2', '2nd Year'),
            ('3', '3rd Year'),
            ('4', '4th Year')],
        validators=[DataRequired()])
    department = SelectField(
        'Department', choices=[
            ('', 'Choose'),
            ('CS', 'Computer Science'),
            ('ENG', 'Engineering'),
            ('BIZ', 'Business'),
            ('ART', 'Arts')],
        validators=[DataRequired()])

    profile_img = FileField(
        'Profile Picture',
        validators=[FileAllowed(
            ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
            'Images only!')])
    laptop_img1 = FileField(
        'Laptop Picture 1',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])
    laptop_img2 = FileField(
        'Laptop Picture 2',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])
    laptop_img3 = FileField(
        'Laptop Picture 3',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])

    submit = SubmitField('Update')
