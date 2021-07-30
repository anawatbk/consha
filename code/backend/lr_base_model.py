import pandas as pd
import numpy as np
import sqlalchemy as db
import sys
import os
import pickle
from pathlib import Path

from sklearn.linear_model import LinearRegression
from sqlalchemy import create_engine, String, Integer
from config import Config
from fuzzy_match import match
from fuzzy_match import algorithims
from collections import Counter

conn = create_engine(Config.SQLALCHEMY_DATABASE_URI)
engine = db.create_engine(Config.SQLALCHEMY_DATABASE_URI)

metadata = db.MetaData(schema='crawled_data')
ewg = db.Table('ewg_product', metadata, autoload=True, autoload_with=engine)


def formatted_ewg_ingredient_score(ewg):
    '''calls the ewg ingredient database and creates array of
    ingredient, score lists.The scores are calculated as the mean
    score for that ingredient,because some ingredients have multiple scores.'''
    query = db.select([ewg])
    result = conn.execute(query).fetchall()
    ewg_df = pd.DataFrame(result, columns=ewg.columns.keys())

    # taking mean of score per ingredient as ingredient score
    ingredient_scores = ewg_df.groupby('ingredient')['ingredient_score'] \
        .apply(np.mean)
    ingredient_scores = np.array(pd.DataFrame(ingredient_scores).reset_index())
    return ingredient_scores


def remove_punct(string):
    '''Removing punctuation from a given string.
    Code from www.geeksforgeeks.org/python-remove-punctuation-from-string/'''
    punc = '''!()-[]{};:'"\, <>./?@#$%^&*_~'''
    for ele in string:
        if ele in punc:
            string = string.replace(ele, "")
    return string


# Fuzzy Matching to match ingredients from amazon with scores from ewg ####
def string_matching(ewg_string, amazon_ingredient):
    '''Matches ewg ingredient strings with amazon ingredient strings.'''
    ewg_string = remove_punct(ewg_string.strip().lower())
    amazon_string = remove_punct(amazon_ingredient.strip().lower())
    match_score = algorithims.cosine(ewg_string, amazon_string)
    if match_score > .55:
        return True
    return False


def ingredient_string_matching(raw_amz_ingredient_list, ewg_ingredient_scores):
    '''Input: raw list of ingredients from amazon - list[str] and
       numpy array of ewg ingredients and score pairs
       Output: list of scores from ewg database - float'''
    ingredient_score_list = []
    for ingredient in raw_amz_ingredient_list:
        for ewg_ingredient, ewg_score in ewg_ingredient_scores:
            if string_matching(ingredient, ewg_ingredient):
                ingredient_score_list.append((ewg_score))
                break
    return ingredient_score_list


# second feature: max_three_mean
def max_three_scores(ingredient_scores):
    '''Creating feature: mean of top three ingredients.'''
    ingredient_scores.sort(reverse=True)
    return np.mean(ingredient_scores[:3])


# third feature(s): a count of each value - going to take int of each
def product_score_count(ingredient_scores):
    '''Creating feature:generates count of each score for a list of scores.'''
    integer_ingredient_scores = [int(i) for i in ingredient_scores]
    count_dictionary = Counter(integer_ingredient_scores)

    # filling in the gaps with 0s
    for i in range(1, 10):
        if not count_dictionary.get(i):
            count_dictionary[i] = 0
    return count_dictionary


def combine_features(sample_amz_ingredient_list, ewg):
    '''
    combine features for score generating model.
    '''
    ewg_ingredient_scores = formatted_ewg_ingredient_score(ewg)
    ingredient_scores = ingredient_string_matching(sample_amz_ingredient_list,
                                                   ewg_ingredient_scores)
    # creating features
    max_three = max_three_scores(ingredient_scores)
    ingredient_count = len(sample_amz_ingredient_list)
    count_dictionary = product_score_count(ingredient_scores)
    # combining and formatting features for model
    x_df = pd.DataFrame(count_dictionary, index=[0])
    x_df['max_three'] = max_three
    x_df['ingredient_count'] = ingredient_count
    x_df.columns = ['ingredient_count', 'max_three_mean',
                    'count_1', 'count_2', 'count_3',
                    'count_4', 'count_5', 'count_6',
                    'count_7', 'count_8', 'count_9']
    return x_df.values.reshape(1, -1)


ewg_ingredient_scores = formatted_ewg_ingredient_score(ewg)


def get_score(lr, amz_ingredient_list):
    '''
    covert asin list to list of product info dictionary

    Parameters
    ----------
    lr : sklearn model
        sklearn model (Random Forest)
    amz_ingredient_list : list
        list of ingredients from amazon

    Returns
    -------
    int
        consha score of 0-10 (lack of ingredients information gets -1)
    '''
    if len(ingredient_string_matching(amz_ingredient_list,
                                      ewg_ingredient_scores)) <= 3:
        return -1
    raw_prediction = round(lr.predict(combine_features(amz_ingredient_list,
                                                       ewg))[0])
    return 10 - raw_prediction
