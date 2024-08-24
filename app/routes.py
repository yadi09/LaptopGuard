from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("welcome to LaptopGuard")
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/index')
def index():
    return render_template('index.html')
