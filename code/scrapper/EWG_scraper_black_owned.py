import pandas as pd
import requests
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# helper functions
def scrape_company_info(category_url):
    """Takes a url for a particular category and returns two things for the 12 items that show up on that page:
    1. A list of dictionaries containing the following information: company, product name, EWG score, link to product page  
    2. A list of hyperlinks to individual product pages (same as the last item in the dictionary)"""

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}

    k = requests.get(category_url).text
    soup=BeautifulSoup(k,'html.parser')
    productslist = soup.find_all("div",{"class":"product-tile"})

    # Build a dictionary for each product info
    black_owned = []

    for product in productslist:
        company = product.find("p", {"class":"product-company"}).text
        black_owned.append(company)

    return black_owned

def load_EWG():
    """Loading the driver"""
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')  # Optional argument, if not specified will search path.
    # opening the web browser
    driver.get('https://www.ewg.org/skindeep/browse/category/Facial_cleanser/?category=Facial+cleanser&minority_owned=Y')
    return driver

def close_popup(driver):
    """Closing EWG specific popup"""
    button = driver.find_element_by_class_name("sidebar-iframe-close")
    button.click()

def click_next(driver):
    """clicking on the next page link"""
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.content > div.flexbox-column-wrapper > main > section:nth-child(4) > div.pages.flex > a.next_page"))).click()

def main():
    """
    Given a product page, accesses each product and pulls name, data available,
    ingredients, concern, company, product_url.
    Saves product information for each product as csv file to Data directory.
    """
    driver = load_EWG()
    # giving page time to load
    time.sleep(4)
    close_popup(driver)

    # accessing each page
    for i in range(5):
        companies = set()
        time.sleep(2)
        # accessing link at each page
        page_url = driver.current_url
        company_page_list = scrape_company_info(page_url)
        df = pd.DataFrame(company_page_list)
        df.to_csv(f"black_owned_brands_{i}.csv", index=False)

        # proceeding to next page of 12 ingredients
        click_next(driver)

    # close browser when finished
    driver.quit()
main()
