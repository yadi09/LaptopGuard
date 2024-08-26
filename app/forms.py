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
        render_kw={"placeholder": "25021/14"})

    gender = SelectField(
        'Gender',
        choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        validators=[DataRequired()])
    year = SelectField(
        'Year',
        choices=[
            ('1', '1st Year'),
            ('2', '2nd Year'),
            ('3', '3rd Year'),
            ('4', '4th Year')],
        validators=[DataRequired()])
    department = SelectField(
        'Department', choices=[
            ('CS', 'Computer Science'),
            ('ENG', 'Engineering'),
            ('BIZ', 'Business'),
            ('ART', 'Arts')],
        validators=[DataRequired()])

    profile_picture = FileField(
        'Profile Picture',
        validators=[FileAllowed(
            ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
            'Images only!')])
    laptop_picture = FileField(
        'Laptop Picture',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
                                'Images only!')])

    submit = SubmitField('Register')
