import requests
import re
import pickle

from config import Config
from backend.lr_base_model import get_score
from backend.recommendation import get_recommendation


def _get_rf_json(url, api_key):
    '''
    Get response json from Rainforest API
    '''
    # asin = re.search(r'dp/([^/]+)', url).group(1)
    asin = re.findall(r'B[A-Z0-9]{9}', url)[0]
    params = {
        'api_key': api_key,
        'type': 'product',
        'amazon_domain': 'amazon.com',
        'asin': asin
    }
    # make the http GET request to Rainforest API
    api_result = requests.get(
        'https://api.rainforestapi.com/request', params)
    # print the JSON response from Rainforest API
    # json_str = json.dumps(api_result.json())
    res_dict = api_result.json()
    return res_dict


def _extract_from_rainforest(result: dict) -> dict:
    """
    Extracts all needed information from Rainforest API request in preparation
    to store in cached_data.amazon_products
    database.
    Lists datatypes converted to patterned strings to avoid headache of d
    atatype declaration in RDS database
    Some of these may need to be tested further (i.e. ingredients,
    skin type, brand) since their location seemed to
    vary for each request

    :return: dictionary with keys being the schema of c
    ached_data.amazon_products
    """
    try:
        target_product = dict()
        info = result['product']

        # asin
        asin = info['asin']
        target_product['asin'] = asin

        # product link
        product_link = info['link']
        target_product['product_link'] = product_link

        # product name
        product_title = info['title']
        target_product['product_title'] = product_title

        # product category
        product_category = info['categories'][-1]['name']
        target_product['product_category'] = product_category

        # product key words
        product_keywords = result['product']['keywords']
        target_product['product_keywords'] = product_keywords

        # price
        target_product['price'] = None
        try:
            target_product['price'] = result['product']['buybox_winner'][
                'price']['value']
        except Exception:
            pass

        # product description
        target_product['product_description'] = 'Not Available'
        if 'description' in info.keys():
            target_product['product_description'] = info['description']
        elif 'a_plus_content' in info.keys():
            if 'company_description_text' in info['a_plus_content'].keys():
                target_product['product_description'] = (
                    info['a_plus_content']['company_description_text'])

        # feature_bullets
        target_product['feature_bullets'] = 'Not Available'
        if 'feature_bullets' in info.keys():
            target_product['feature_bullets'] = info['feature_bullets_flat']

        # image_url
        image_url = info['main_image']['link']
        target_product['image_url'] = image_url

        # ingredients
        target_product['ingredients'] = 'Not Available'
        if 'important_information' in info.keys():
            for important_info in info['important_information']['sections']:
                if ('title' in important_info.keys(
                ) and important_info['title'] == 'Ingredients'):
                    ingredients = important_info['body']
                    target_product['ingredients'] = ingredients
                    target_product['ingredients'] = target_product[
                        'ingredients'].split(',')
                    target_product['ingredients'] = [
                        item.strip() for item in target_product['ingredients']
                        ]

        # pulled from "attributes" subdirectory
        skin_type = "Not Available"
        brand = "Not Available"
        if 'attributes' in info.keys():
            for attr in info['attributes']:
                if attr['name'] == 'Skin Type':
                    skin_type = attr['value']
                if attr['name'] == 'Brand':
                    brand = attr['value']
        target_product['skin_type'] = skin_type
        target_product['brand'] = brand

        return target_product
    except Exception as e:
        print(type(e), e)
        return None


def get_result(url, amazon_product_embeddings, lr, api_key=Config.API_KEY):
    '''
    Get relevance product information, score, and recommendation list
    Parameters
    ----------
    url : str
        amazon url (only moiturizer)
    api_key : str
        RainForest API key

    Returns
    -------
    dict
        return all information required for front-end in dictionary format
    '''
    response = _get_rf_json(url, api_key)  # get json from rainforest
    product_data = _extract_from_rainforest(response)
    # preprocess description
    if len(product_data['product_description']) < len(
            product_data['feature_bullets']):
        description = product_data['feature_bullets']
    else:
        description = product_data['product_description']

    description = f"Skin Condition {product_data['skin_type']} {description}"
    replace = (('\n', ' '), ('product description', ''),
               (product_data['brand'], ''))
    for element in replace:
        description = re.sub(
            element[0],
            element[1],
            description, flags=re.IGNORECASE)
    return {'asin': product_data['asin'],
            'title': product_data['product_title'],
            'product_link': product_data['product_link'],
            'image_url': product_data['image_url'],
            'price': product_data['price'],
            'product_keywords': product_data['product_keywords'],
            'score': get_score(lr, product_data['ingredients']),
            'recommendations': get_recommendation(
                description, amazon_product_embeddings),
            'ingredient': product_data['ingredients'],
            'desc': description
            }
