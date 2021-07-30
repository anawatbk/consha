import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_table(link: str) -> pd.DataFrame:
    """
    Given a product link, pulls ingredient concerns, reformats layout, and returns a pandas dataframe.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}
    k = requests.get(link, headers=headers).text
    soup = BeautifulSoup(k, 'html.parser')
    table = soup.find("table", {"class":"table-ingredient-concerns"})
    rows = []
    for row in table.find("tbody").find_all("tr"):
        attribs = row.find_all("td")
        score_link = attribs[0].find("img")['src']
        score = int(score_link.split('/')[-1].split('-')[1])
        data_avail = attribs[1].find('span').text
        ingredient = attribs[2].find("a").text
        concerns = attribs[3].find("div").find("p").text.split('•')
        if len(concerns) > 1:
            redact = 'meets restrictions and warnings based on EWG review of company data'
            concerns = [c.strip() for c in concerns[1:] if redact not in c]
        else:
            concerns = list()
        rows.append([score, data_avail, ingredient, concerns])

    return pd.DataFrame(rows, columns=['Score', 'Data Availability', 'Ingredient', 'Concern'])

# Use Case:
# product_link = 'https://www.ewg.org/skindeep/products/902120-Beautycounter_Countertime_Lipid_Defense_Cleansing_Oil_/'
# print(scrape_table(product_link))