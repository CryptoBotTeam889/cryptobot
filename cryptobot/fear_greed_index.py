import numpy as np
import pandas as pd
from datetime import datetime
import requests

'''
Creates a pandas dataframe with the fear_greed_index
Columns
- [value] between 0 (extreme fear) and 100 (extreme greed)
- [value_classification] been extreme fear, fear, neutral, greed and extreme greed
- timestamp in ms
more information at https://alternative.me/crypto/fear-and-greed-index/
'''
FIRST_DATE = datetime.strptime('2018-02-01', '%Y-%m-%d')
RAW_DATA_PATH = './data/fear_greed_index.csv'

def fear_greed_index(initial_date):
    '''
    gets data from the api
    initial date = initial data to start gathering the index. Oldest data possible 2018-02-01
    '''
    #input for firs date = YYYY/MM/DD
    date = datetime.strptime(initial_date, '%Y-%m-%d')

    if date>= FIRST_DATE:
        today = date.today()
        num_days = (today - date)
        #URL for scraping
        URL = f'https://api.alternative.me/fng/?limit={num_days.days}'

        api_data = requests.get(URL).json()
        fear_greed_df = pd.DataFrame(api_data['data'])
        fear_greed_df = fear_greed_df.drop(columns=['time_until_update'])
        fear_greed_df.to_csv(RAW_DATA_PATH)

    else:
        print(f'Initial date should be greater than {FIRST_DATE.strftime("%Y-%m-%d")}')

    return fear_greed_df

def read_fear_and_greed():
    '''
    reads the fear_greed_index.csv file and returns a pandas dataframe
    '''

    fear_greed_df = pd.read_csv(RAW_DATA_PATH)
    return  fear_greed_df
