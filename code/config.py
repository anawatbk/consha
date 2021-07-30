import os
basedir = os.path.abspath(os.path.dirname(__file__))
dbuser = os.environ['DBUSER']
dbpwd = os.environ['DBPWD']
api_key = os.environ['API_KEY']

class Config(object):
    SECRET_KEY = os.urandom(24)  # For WTF forms
    SQLALCHEMY_DATABASE_URI = f'postgresql://{dbuser}:{dbpwd}@msds603.cm9lzsru7xeh.us-west-2.rds.amazonaws.com/conshadb'
    # flash-login uses session which require a secret
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    API_KEY = api_key
