import logging


import azure.functions as func
import requests #html requests
from bs4 import BeautifulSoup
#TODO: take in information from js page, then set scraped price as original price and current price, then input it into sql database

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f'{name} : {scrape_price(name)}')
    else:
        return func.HttpResponse(
             f'Input a price',
             status_code=200
        )

def scrape_price(URL: str):
    headers = ({'User-Agent':
            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})

    page = requests.get(URL, headers=headers) #response.text gets page and html
    soup = BeautifulSoup(page.text, 'html.parser')

    price_tag = soup.find(id='priceblock_ourprice')
    price = price_tag.get_text()
    #gets the lowest price if a range is listed
    if('-' in price):
        price = price[:price.index('-')]

    #turn into number
    price = price.replace('$', '')
    price = float(price)
    return price