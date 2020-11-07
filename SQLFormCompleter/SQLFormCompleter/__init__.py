 import logging
import azure.functions as func

import requests #html requests
from bs4 import BeautifulSoup

import pyodbc

#TODO: sql only changes the second row in db, changes that rather than adding new row
server = 'bitcamp.database.windows.net'
database = 'PriceScraper'
username = 'fi.leul3562'
password = 'Mrs.McKitty101'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    phonenumber = req.params.get('phonenumber')
    url = req.params.get('url')
    baseline_percentage = req.params.get('baseline_percentage')
    duration = req.params.get('duration')
    
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            url = req_body.get('url')
    
    if not url or scrape_price(url) == 'incompatible':
        return func.HttpResponse(
             f'Unable to scrape price. Try another link',
             status_code=200
        )
        return
    price = scrape_price(url)
    if url and phonenumber and baseline_percentage and duration:
       updatedInfo = update_database(url, phonenumber, baseline_percentage, duration, price, price)
       #print("URL: {}\nNUM: {}\nPERCENT: {}\nDUR: {}\nORIG: {}\nCURR:{}".format(url, phonenumber, baseline_percentage, duration, price, price)
       return func.HttpResponse(
             updatedInfo,
             status_code=200
        )
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
    if price_tag is None:
        price_tag = soup.find(id='priceblock_dealprice')
    if price_tag is None:
        return "incompatible"
    price = price_tag.get_text()
    #gets the lowest price if a range is listed
    if('-' in price):
        price = price[:price.index('-')]

    #turn into number
    price = price.replace('$', '')
    price = float(price)
    return price

def update_database(url:str, phonenumber:int, baseline_percentage:float, duration:float, original_price, current_price):
    row_str = ''
    cursor.execute("INSERT INTO dbo.ScrapedData VALUES (?,?,?,?,?,?)", phonenumber, baseline_percentage, duration, original_price, current_price, url) 
    
    cnxn.commit()
    cursor.execute('''WITH removing AS (
    SELECT 
        phonenumber, 
        baseline_percentage, 
        duration, 
        original_price,
        current_price, 
        link,
        ROW_NUMBER() OVER (
            PARTITION BY 
                phonenumber,  
                link
            ORDER BY 
                phonenumber, 
                link
        ) row_num
        FROM 
            dbo.ScrapedData
        )
        DELETE FROM removing
        WHERE row_num > 1;''')

    cnxn.commit()
    cursor.execute('''WITH removing AS (
    SELECT 
        phonenumber, 
        baseline_percentage, 
        duration, 
        original_price,
        current_price, 
        link,
        ROW_NUMBER() OVER (
            PARTITION BY 
                phonenumber,  
                link
            ORDER BY 
                phonenumber, 
                link
        ) row_num
        FROM 
            dbo.ScrapedData
        )
        DELETE FROM removing
        WHERE row_num > 1;''')
    cnxn.commit()
    cursor.execute("SELECT * FROM [PriceScraper].[dbo].[ScrapedData]")
    cnxn.commit()
    row = cursor.fetchone()
    while row:
        row_str = row_str + row.__repr__() + '\n'
        row = cursor.fetchone()
    return row_str
