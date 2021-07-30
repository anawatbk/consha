import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from product_page_scraper import *
from product_detail_scraper import *


# helper functions
def load_EWG():
    """Loading the driver"""
    driver = webdriver.Chrome('/usr/local/bin/chromedriver')  # Optional argument, if not specified will search path.
    # opening the web browser
    driver.get('https://www.ewg.org/skindeep/browse/category/Facial_cleanser/')
    return driver


def close_popup(driver):
    """Closing EWG specific pop-up"""
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
    for i in range(95):
        time.sleep(2)
        # accessing link at each page
        page_url = driver.current_url
        product_page_list = scrape_product_info(page_url)

        for index, product_dict in enumerate(product_page_list):
            time.sleep(2)
            product_url = product_dict['link']
            # use product url to scrape table information
            product_df = scrape_table(product_url)

            # combine ingredient information with product information
            product_df['product_name'] = product_dict['name']
            product_df['company'] = product_dict['company']
            product_df['product_url'] = product_url

            # save csv for each product
            product_df.to_csv(f'Data/product{i}.{index}.csv', index=False)
        # proceeding to next page of 12 ingredients
        click_next(driver)

    # close browser when finished
    driver.quit()
main()
