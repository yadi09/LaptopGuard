from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FileField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=15)])  # Username field with validation
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=4, max=16)])  # Password field with validation
    remember_me = BooleanField('Remember Me')  # Checkbox to remember login
    Login = SubmitField('Login')  # Submit button


class RegistrationForm(FlaskForm):
    fullname = StringField(
        'Full Name', validators=[DataRequired(), Length(min=1, max=20)])  # Full name input
    studentId = StringField(
        'Student ID',
        validators=[DataRequired(), Length(max=20)],
        render_kw={"placeholder": "25021"})  # Student ID with a placeholder

    gender = SelectField(
        'Gender',
        choices=[('', 'Choose'),('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        validators=[DataRequired()])  # Gender dropdown
    year = SelectField(
        'Year',
        choices=[
            ('', 'Choose'),
            ('1', '1st Year'),
            ('2', '2nd Year'),
            ('3', '3rd Year'),
            ('4', '4th Year')],
        validators=[DataRequired()])  # Year dropdown
    department = SelectField(
        'Department', choices=[
            ('', 'Choose'),
            ('CS', 'Computer Science'),
            ('ENG', 'Engineering'),
            ('BIZ', 'Business'),
            ('ART', 'Arts')],
        validators=[DataRequired()])  # Department dropdown

    profile_img = FileField(
        'Profile Picture',
        validators=[DataRequired(), FileAllowed(
            ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
            'Images only!')])  # Profile image upload
    laptop_img1 = FileField(
        'Laptop Picture 1',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])  # Laptop picture 1
    laptop_img2 = FileField(
        'Laptop Picture 2',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')]) # Laptop picture 2
    laptop_img3 = FileField(
        'Laptop Picture 3',
        validators=[DataRequired(), FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])  # Laptop picture 3

    submit = SubmitField('Register')  # Submit button



class SearchForm(FlaskForm):
    student_id = StringField('Student ID', validators=[DataRequired()])  # Input for student ID
    submit = SubmitField('Search')  # Submit button for search



class UpdateStudentForm(RegistrationForm):
    """
    fullname = StringField(
        'Full Name', validators=[DataRequired(), Length(min=1, max=20)])  # Full name input
    studentId = StringField(
        'Student ID',
        validators=[DataRequired(), Length(max=20)])  # Student ID input

    gender = SelectField(
        'Gender',
        choices=[('', 'Choose'),('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        validators=[DataRequired()])  # Gender dropdown
    year = SelectField(
        'Year',
        choices=[
            ('', 'Choose'),
            ('1', '1st Year'),
            ('2', '2nd Year'),
            ('3', '3rd Year'),
            ('4', '4th Year')],
        validators=[DataRequired()])  # Year dropdown
    department = SelectField(
        'Department', choices=[
            ('', 'Choose'),
            ('CS', 'Computer Science'),
            ('ENG', 'Engineering'),
            ('BIZ', 'Business'),
            ('ART', 'Arts')],
        validators=[DataRequired()])  # Department dropdown
    """

    profile_img = FileField(
        'Profile Picture',
        validators=[FileAllowed(
            ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff', 'svg'],
            'Images only!')])  # Profile picture upload
    laptop_img1 = FileField(
        'Laptop Picture 1',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])  # Laptop picture 1
    laptop_img2 = FileField(
        'Laptop Picture 2',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])  # Laptop picture 2
    laptop_img3 = FileField(
        'Laptop Picture 3',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif',
                                 'bmp', 'tiff', 'svg'],
                                'Images only!')])  # Laptop picture 3
    

    submit = SubmitField('Update')  # Submit button for updating student info



