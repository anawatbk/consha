from app import application, classes, db, amazon_product_embeddings, lr
from flask import render_template, redirect, url_for
from flask import get_flashed_messages, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField, StringField, SelectField
from wtforms.validators import URL, Length, DataRequired, InputRequired
from flask_login import current_user, login_user, login_required, logout_user
import os
import re

from backend.get_result import get_result


class URLForm(FlaskForm):
    """
    Accepts a product url.
    """
    website = StringField(
        'Product URL',
        validators=[InputRequired()]
    )
    submit = SubmitField('Submit')


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index():
    """
    Index page: Renders a webpage with a link entry box and a submit button

    This page should redirect to "display recommendations" with the api call
    and all the relevant information
    """
    form = URLForm()
    if form.validate_on_submit():
        url = form.website.data
        if 'https://' in url:
            url = url[8:].replace('/', '%')
        return redirect(url_for('recommendations',
                                filler='page',
                                product_url=url))

    return render_template('index.html', form=form)


@application.route('/upload', methods=['GET', 'POST'])
def upload():
    """
    Upload page: Take in ULR from Amazon to render recommendation page
    """
    form = URLForm()

    if form.validate_on_submit():
        url = form.website.data
        if 'https://' in url:
            url = url[8:].replace('/', '%')
        return redirect(url_for('recommendations',
                                filler='page',
                                product_url=url))

    return render_template('upload_test.html', form=form)


@application.route('/recommendations/<filler>&url=<product_url>',
                   methods=['GET', 'POST'])
def recommendations(filler, product_url):
    """
    1) Takes in the product link and calls the API (rainforest or "fake"
       use case)
    2) Determine EWG score either by RDS database or ML model

    3) Two cases:
        a. If the product has a sufficiently good score, return product image,
           description, and link to it.
        b. If product is no good, look up scores of recommended products and
           provide a list of product/description/values
    """

    result = get_result(product_url, amazon_product_embeddings, lr)

    return render_template('recommendations.html',
                           recs_list=result['recommendations'],
                           product_score=result['score'])


@application.route('/recommendations_test/<filler>&url=<product_url>',
                   methods=['GET', 'POST'])
def recommendations_test(filler, product_url):
    """
    Test backend function
    available keys
    ['asin', 'title', 'product_link', 'image_url',
    'price', 'product_keywords', 'score',
    'recommendations','ingredient', 'desc']
    """
    result = get_result(product_url, amazon_product_embeddings, lr)

    return f"""<p>f{result['recommendations']} </br>
                  f{result['desc']} </br>
            </p>"""


# Login system
@application.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register: Allow user to register with username, email, and password
    """

    registration_form = classes.RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        email = registration_form.email.data
        password = registration_form.password.data
        check_user = classes.User.query.filter_by(username=username).first()
        check_email = classes.User.query.filter_by(email=email).first()
        if check_user:
            flash('Username already exist')
            return render_template('register.html', form=registration_form)
        elif check_email:
            flash('Email already exist')
            return render_template('register.html', form=registration_form)
        else:
            user = classes.User(username, email, password)
            db.session.add(user)
            db.session.commit()
            return render_template('registered.html')
    return render_template('register.html', form=registration_form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login: Allow user to login with username and password
    """

    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        # Look for it in the database.
        user = classes.User.query.filter_by(username=username).first()

        # Login and validate the user.
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('logged_in'))

    return render_template('login.html', form=login_form)


@application.route('/logged_in')
def logged_in():
    """
    Logged in: Display page once user logged in
    """

    return render_template('logged_in.html', user=current_user.username)


@application.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    """
    Log Out: Display page once user logged out
    """
    logout_user()
    return render_template('logout.html')
