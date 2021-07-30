import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product_info(category_url):
    """Takes a url for a particular category and returns two things for the 12 items that show up on that page:
    1. A list of dictionaries containing the following information: company, product name, EWG score, link to product page  
    2. A list of hyperlinks to individual product pages (same as the last item in the dictionary)"""


    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

    k = requests.get(category_url).text
    soup=BeautifulSoup(k,'html.parser')
    productslist = soup.find_all("div",{"class":"product-tile"})

    # Build a dictionary for each product info
    products = []

    # List of just links for Okeefe
    links = []

    for product in productslist:
        product_info = {} # Initialze new product dictionary for each product
        
        # Get brand
        company = product.find("p", {"class":"product-company"}).text
        product_info["company"] = company
        
        # Get name
        product_name = product.find("p", {"class":"product-name"}).text
        product_info["name"] = product_name
        
        # Get score 
        if product.find("img", {"class":"product-score-img verified"}): # For EWG verified products 
            score = product.find("img", {"class":"product-score-img verified"}).get("src")
        else:
            score = product.find("img",{"class":"product-score-img squircle"}).get("src") # For all other products that get a score 

        score = score.partition("score-")[2].rpartition("-")[0] # Extract just the score from the src url 
        product_info["score"] = score

        products.append(product_info)

        # Get link to product-specific url
        link = product.find("a").get("href")
        product_info["link"] = link
        links.append(link)

    return products

#
# category_url = "https://www.ewg.org/skindeep/browse/category/Facial_cleanser/"
# results = scrape_product_info(category_url)

# print(links)
# print(results)