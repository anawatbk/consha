import os
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pandas as pd
import pickle

# Initialization
# Create an application instance (an object of class Flask)  which
# handles all requests.
application = Flask(__name__)
application.config.from_object(Config) # set Flask App config from config.py
db = SQLAlchemy(application) # initiate db
db.create_all() # create table
db.session.commit() # commit

# login_manager needs to be initiated before running the app
login_manager = LoginManager()
login_manager.init_app(application)

# load embedding and model to memory
amazon_product_embeddings = pd.read_pickle('./backend/model/amazon_product_embeddings.sav')
filename = './backend/model/finalized_RF.sav'
lr = pickle.load(open(filename, 'rb'))

# Added at the bottom to avoid circular dependencies. (Altough it violates PEP8 standards)
from app import classes
from app import routes
