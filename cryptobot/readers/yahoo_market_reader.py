from enum import Enum
import logging
import yfinance as yf
import pandas as pd
from datetime import datetime

from cryptobot.brokers.enums import Intervals


class YahooMarketReader:
    """
    The goal of this reader is to get the data from the api once and then keep it in memory.
    So, after initialize the object we have to use the get_data method.
    TODO Use cache to store the data in memory.
    """

    class YahooSymbol(Enum):
        """
        This enum is to track the Yahoo symbols that we actually support.

        '^IXIC' - Nasdaq compound index
        '^GSPC' - S&P 500 index
        'GC=F' - Gold
        '^DJI' - Dow Jones Industrial Average
        '^TNX' = S&P 500 US T-bills (10 year)
        'DX-Y.NYB'= US Dollar/USDX - Index - Cash
        """

        IXIC = "^IXIC"
        GSPC = "^GSPC"
        GC_F = "GC=F"
        DJI = "^DJI"
        TNX = "^TNX"
        DXY_NYB = "DX-Y.NYB"

    def __init__(self, start_date: datetime, end_date: datetime):
        indices = [s for s in self.YahooSymbol]

        df = None
        for index in indices:
            df_aux = self.get_yahoo_data(index, start_date, end_date)
            df_aux = self.parse_data(df_aux, index)
            df = (
                df_aux
                if df is None
                else df.merge(df_aux, on="close_time_day", how="left")
            )

        self.data = df

    def get_data(self):
        return self.data

    @classmethod
    def get_yahoo_data(
        cls, symbol: YahooSymbol, start_date: datetime, end_date: datetime
    ):
        """
        This function returns the historical data of a determime symbol (check https://finance.yahoo.com/)
        and start_date (YYYY-MM-DD) and end_date (YYYY-MM-DD) for the time series, the period of the date is 1d
        """
        logging.info(f"Getting data about {symbol.value} from Yahoo Finances")

        ticker = yf.Ticker(symbol.value)

        df = ticker.history(
            interval=Intervals.ONE_DAY.value,
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
        )

        df = df.reset_index()
        df = df.drop(columns=["Dividends", "Stock Splits", "Volume"])
        df["timestamp"] = df["Date"].apply(lambda x: x.timestamp())

        columns = df.columns
        new_columns = []
        for column in columns:
            new_columns.append(f"{symbol.value}_{str(column)}")

        df.columns = new_columns

        return df

    @classmethod
    def parse_data(cls, df, symbol: YahooSymbol):
        index = symbol.value
        df[f"{index}_Date"] = df[f"{index}_Date"].apply(
            lambda x: x.strftime("%Y-%m-%d")
        )
        df.rename(columns={f"{index}_Date": "close_time_day"}, inplace=True)
        df[f"{index}_avg"] = (
            df[f"{index}_Open"]
            + df[f"{index}_Close"]
            + df[f"{index}_High"]
            + df[f"{index}_Low"] / 4
        )
        df.drop(
            columns=[
                f"{index}_timestamp",
                f"{index}_Open",
                f"{index}_Close",
                f"{index}_High",
                f"{index}_Low",
            ],
            inplace=True,
        )
        return df
