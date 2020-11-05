import logging
import azure.functions as func

import requests #html requests
from bs4 import BeautifulSoup

import pyodbc

#TODO: sql only changes the second row in db, changes that rather than adding new row

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
     
     
    server = 'bitcamp.database.windows.net'
    database = 'PriceScraper'
    username = 'fi.leul3562'
    password = 'Mrs.McKitty101'
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    cursor = cnxn.cursor()
    row_str = ""

    

    

   
    phonenumber = req.params.get('phonenumber')
    url = req.params.get('url')
    baseline_percentage = req.params.get('baseline_percentage')
    duration = req.params.get('duration')
    
    cursor.execute("INSERT INTO dbo.ScrapedData VALUES (?,?,?,?,?,?)", phonenumber, baseline_percentage, duration, scrape_price(url), scrape_price(url), url) 
    cnxn.commit()
    cursor.execute("SELECT * FROM [PriceScraper].[dbo].[ScrapedData]")

    row = cursor.fetchone()
    while row:
        row_str += row.__repr__() + "\n"
        row = cursor.fetchone()
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            url = req_body.get('url')

    if url and phonenumber:
        #resp = '{} : {}, phonenumber : {}'.format(url, scrape_price(url), phonenumber)
        return func.HttpResponse(row_str)
    
    elif url:
        return func.HttpResponse(row_str)
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
