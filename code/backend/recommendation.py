import sys
import os

from sqlalchemy import create_engine, String, Integer
import pandas as pd
import numpy as np
import re
import pickle
from sentence_transformers import SentenceTransformer, util

from config import Config

conn = create_engine(Config.SQLALCHEMY_DATABASE_URI)
model = SentenceTransformer('paraphrase-MiniLM-L12-v2')


def _get_recommendation_asin(description, amazon_product_embeddings,
                             threshold, n):
    '''
    Get recommendation list (in asin format)
    Parameters
    ----------
    description : str
        product description
    amazon_product_embeddings : pd.DataFrame
        description embeddings of all amazon product
    threshold : int
        lower threshold of consha score (consha_score > threshold)
    n : int
        number of product return

    Returns
    -------
    list
       recommendation list (in asin format)
    '''
    query = f"""
    SELECT * FROM cached_data.amz_score WHERE consha_score > {threshold}"""
    amz_score_df = pd.read_sql(query, con=conn)
    # print(description)
    if len(amz_score_df) > 0:
        amz_score_df = amz_score_df.join(
            amazon_product_embeddings.set_index('asin'), on='asin')
        amz_score_df = (
            amz_score_df[~amz_score_df['embedding'].isnull()].copy())
        input_embedding = model.encode(description, convert_to_tensor=True)
        sim_score = util.pytorch_cos_sim(
            input_embedding,
            amz_score_df['embedding'].reset_index(drop=True)).flatten()
        amz_score_df['sim_score'] = sim_score
        max_score = max(sim_score).item()
        alpha = 0.7  # weight of similarity score
        amz_score_df['final_score'] = alpha * (
            amz_score_df['sim_score'] / max_score) + (
            1-alpha) * (amz_score_df['consha_score'] / 10)
        return amz_score_df.sort_values(
            by='final_score', ascending=False)['asin'][:n].to_list()
    else:
        return None


def _get_info_from_asin(asin):
    '''
    covert asin product info dictionary
    Parameters
    ----------
    asin : str
        amazon asin

    Returns
    -------
    dict
        product info dictionary
    '''
    query = f"""
    SELECT t1.asin, title, product_link,
           image_url, price, product_keywords, consha_score
    FROM cached_data.amazon_product_500 as t1
    JOIN cached_data.amz_score as t2
    ON t1.asin = t2.asin
    WHERE t1.asin = '{asin}';"""
    data = pd.read_sql(query, con=conn)
    return data.to_dict('records')[0]


def get_recommendation(description, amazon_product_embeddings,
                       threshold=7, n=3):
    '''
    covert asin list to list of product info dictionary

    Parameters
    ----------
    description : str
        product description
    amazon_product_embeddings : pd.DataFrame
        description embeddings of all amazon product
    threshold : int (default=7)
        lower threshold of consha score (consha_score > threshold)
    n : int (default=3)
        number of product return

    Returns
    -------
    list of dict
        list of product info dictionary
    '''
    asin_list = _get_recommendation_asin(
        description, amazon_product_embeddings, threshold, n)
    if asin_list is not None:
        return [_get_info_from_asin(item) for item in asin_list]
    else:
        return None
