from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired

from app import db, login_manager


class User(db.Model, UserMixin):
    '''
    User table (sqlalchemy)
    '''
    __table_args__ = {'schema': 'website_data'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class AmazonScores(db.Model, UserMixin):
    '''
    amz_score table (sqlalchemy)
    '''
    __table_args__ = {'schema': 'cached_data'}
    __tablename__ = 'amz_score'
    asin = db.Column(db.String(20), primary_key=True)
    score = db.Column(db.Integer)


class EWG(db.Model, UserMixin):
    '''
    ewg_product table (sqlalchemy)
    '''
    __table_args__ = {'schema': 'crawled_data'}
    __tablename__ = 'ewg_product'
    id = db.Column(db.Integer, primary_key=True)
    ingredient_score = db.Column(db.Integer)
    data_availability = db.Column(db.String(255))
    ingredient = db.Column(db.String(80))
    ingredient_concerns = db.Column(db.String(1000))
    product_name = db.Column(db.String(255))
    company = db.Column(db.String(255))
    product_url = db.Column(db.String(1000))
    product_score = db.Column(db.String(100))


class Amazon(db.Model, UserMixin):
    '''
    amazon_product_500 table (sqlalchemy)
    '''
    __table_args__ = {'schema': 'cached_data'}
    __tablename__ = 'amazon_product_500'
    asin = db.Column(db.String, primary_key=True)
    title = db.Column(db.String)
    ingredient = db.Column(db.String)
    category = db.Column(db.String)
    brand = db.Column(db.String)
    skin_type = db.Column(db.String)
    product_link = db.Column(db.String)
    image_url = db.Column(db.String)
    description = db.Column(db.String)
    feature_bullets = db.Column(db.String)
    # price = db.Column(db.Float)
    # rating = db.Column(db.Float)
    # ranks = db.Column(db.String)
    # related_asin = db.Column(db.String)

    def add_values(self,
                   asin,
                   title,
                   ingredient,
                   category,
                   brand,
                   skin_type,
                   product_link,
                   image_url,
                   description,
                   feature_bullets):
        self.asin = asin
        self.title = title
        self.ingredient = ingredient
        self.category = category
        self.brand = brand
        self.skin_type = skin_type
        self.product_link = product_link
        self.image_url = image_url
        self.description = description
        self.feature_bullets = feature_bullets

        # WE USED TO HAVE THESE ATTRIBUTES BUT CURRENTLY DON'T HAVE THEM
        # self.product_keywords = product_keywords
        # self.price = price
        # self.rating = rating
        # self.ranks = ranks
        # self.related_asin = related_asin

# if we didn't find the product in our database
# result = api_call()
# info = extract_info(result) --> dictionary
# classes.Amazon.put(**info)


class RegistrationForm(FlaskForm):
    '''
    RegistrationForm
    '''
    username = StringField('Username:', validators=[DataRequired()])
    email = StringField('Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LogInForm(FlaskForm):
    '''
    LoginForm
    '''
    username = StringField('Username:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    submit = SubmitField('Login')


@login_manager.user_loader
def load_user(id):
    '''
    load user
    '''
    return User.query.get(int(id))


db.create_all()
db.session.commit()
