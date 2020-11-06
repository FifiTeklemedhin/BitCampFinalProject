import datetime
import logging

import azure.functions as func

import pyodbc

server = 'bitcamp.database.windows.net'
database = 'PriceScraper'
username = 'fi.leul3562'
password = 'Mrs.McKitty101'
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('DATA: %s', get_Database_Information())

def get_Database_Information():
    cursor.execute('SELECT phonenumber,link,original_price FROM dbo.ScrapedData;')
    row = cursor.fetchone()
    row_str = ""
    while row:
        row_str += row.__repr__() + "\n"
        row = cursor.fetchone()
    return row_str
