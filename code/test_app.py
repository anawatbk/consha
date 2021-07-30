from app import application
import pickle
from backend.lr_base_model import get_score


def test_application():
    '''
    test if application is available
    '''
    assert application is not None


def UserFromDB(username):
    user = classes.User.query.filter_by(username=username).first()
    return user


def test_db_existence():
    """
    Check whether the __init__ created a db and user class table.
    """
    db = SQLAlchemy()
    engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI, {})
    inspect = db.inspect(engine)
    assert (inspect.has_table("user"))


def test_UserFromDB():
    """
    Assuming that "test, test@gmail.com" is always in the database
    Good to have a test user account
    """
    assert UserFromDB("test").email == "test@gmail.com"
    assert UserFromDB("test").username == "test"


def test_cached_data():
    """
    Ensure that there is data inside the cached amazon information
    """
    cached_products = classes.Amazon.query.all()

    assert len(cached_products) > 0


def test_result():
    """
    test that a valid amazon URL returns parameters for recommendation.html
    """

    url = 'https://www.amazon.com/WRINKLE-PEPTIDE-MOISTURIZER-MATRIXYL' +\
          '-ARGIRELINE/dp/B000GF1E54'
    result = get_result(url,
                        amazon_product_embeddings,
                        lr,
                        api_key=Config.API_KEY)

    assert type(result) == dict
    assert len(result.keys()) == 10


def test_regression_model_trained():
    """
    tests to see if __init__ opened a trained model
    """

    attrs = [v for v in vars(lr)
             if v.endswith("_") and not v.startswith("__")]

    assert len(attrs) != 0


def test_get_score():
    '''
    test if model is serving correct
    results '''
    test_ingredients = ['GLYCERIN', 'SILICA',
                        'DIMETHICONE', 'PEG-100 STEARATE',
                        'GLYCERYL STEARATE',
                        'AMMONIUM POLYACRYLOYLDIMETHYL TAURATE',
                        'ASCORBYL GLUCOSIDE', 'BENZYL ALCOHOL',
                        'BENZYL SALICYLATE']
    filename = 'backend/model/finalized_RF.sav'
    rf = pickle.load(open(filename, 'rb'))
    assert get_score(rf, test_ingredients) == 9
