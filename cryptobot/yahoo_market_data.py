import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_yahoo_data(symbol, start_date, end_date):
    '''
    This function returns the historical data of a determime symbol (check https://finance.yahoo.com/)
    and start_date (YYYY-MM-DD) and end_date (YYYY-MM-DD) for the time series, the period of the date is 1d
    Some usefull symbols:
        '^IXIC' - Nasdaq compound index
        '^GSPC' - S&P 500 index
        'GC=F' - Gold
        '^DJI' - Dow Jones Industrial Average
        '^TNX' = S&P 500 US T-bills (10 year)
        'DX-Y.NYB'= US Dollar/USDX - Index - Cash

    '''

    ticker = yf.Ticker(symbol)

    df = ticker.history(interval='1d', start= start_date, end= end_date)
    df = df.reset_index()
    df = df.drop(columns= ['Dividends','Stock Splits', 'Volume'])
    df['timestamp'] = df['Date'].apply(lambda x: x.timestamp())
    return df
