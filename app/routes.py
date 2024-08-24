from app import app
from flask import render_template


@app.route('/')
def index():
    return render_template("all_student.html", title="All Student")

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)
