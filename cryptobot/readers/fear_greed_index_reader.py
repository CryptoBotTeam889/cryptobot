import logging
import os
import pandas as pd
from datetime import datetime, date
import requests

"""
Creates a pandas dataframe with the fear_greed_index
Columns
- [value] between 0 (extreme fear) and 100 (extreme greed)
- [value_classification] been extreme fear, fear, neutral, greed and extreme greed
- timestamp in ms
more information at https://alternative.me/crypto/fear-and-greed-index/
"""


class FearGreedIndexReader:
    """
    The goal of this reader is to get the data from the api once and then keep it in memory.
    So, after initialize the object we have to use the get_data method.
    TODO Use cache to store the data in memory.
    """

    FIRST_DATE = datetime.strptime("2018-02-01", "%Y-%m-%d")
    DATA_API = os.getenv("FEAR_GREED_INDEX_API")

    def __init__(self, initial_date=FIRST_DATE):
        self.data = self.fear_greed_index(initial_date)

    def get_data(self):
        return self.data

    @classmethod
    def fear_greed_index(cls, initial_date: datetime):
        """
        gets data from the api
        initial date = initial data to start gathering the index. Oldest data possible 2018-02-01
        """
        logging.info(f"Getting data from {cls.DATA_API} from {initial_date}")

        if initial_date >= cls.FIRST_DATE:
            today = date.today()
            num_days = today - initial_date.date()

            api_data = requests.get(
                cls.DATA_API, params={"limit": num_days.days}
            ).json()
            fear_greed_df = pd.DataFrame(api_data["data"])
            fear_greed_df = cls.parse_data(fear_greed_df)
            return fear_greed_df

        else:
            raise ValueError(
                f'Initial date should be greater than {cls.FIRST_DATE.strftime("%Y-%m-%d")}'
            )

    @classmethod
    def parse_data(cls, df):
        """
        Parses and cleans the data from the API
        """
        df["timestamp"] = df["timestamp"].apply(
            lambda x: datetime.utcfromtimestamp(int(x))
        )
        df["close_time_day"] = df["timestamp"].apply(lambda x: x.strftime("%Y-%m-%d"))
        df.drop(columns=["timestamp", "time_until_update"], inplace=True)
        df.columns = ["FG_value", "FG_val_clasif", "close_time_day"]
        df["FG_value"] = df["FG_value"].astype(float)

        return df
