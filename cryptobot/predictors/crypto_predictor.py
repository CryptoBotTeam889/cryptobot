from datetime import datetime, timedelta
import os

import pandas as pd
from cryptobot.brokers.binance_client import BinanceClient
from cryptobot.brokers.enums import Intervals, Symbols
from cryptobot.data import (
    add_target,
    clean_data,
    get_binance_dominance_data,
    get_candles_from_binance,
)
from cryptobot.readers.fear_greed_index_reader import FearGreedIndexReader
from cryptobot.readers.yahoo_market_reader import YahooMarketReader
from cryptobot.utils.feature_engineering import add_metrics
from cryptobot.utils.model_name_helper import generate_latest_model_path
from cryptobot.utils.pipeline_helper import create_pipeline
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model


class CryptoPredictor:

    trained_models = [Symbols.ETHUSDT]

    limit_by_interval = {Intervals.ONE_HOUR: 168 + 200}

    def __init__(self):

        self.models = {}
        self.preprocessors = {}

        for symbol in self.trained_models:
            self.models[symbol] = load_model(generate_latest_model_path(symbol))

        one_year_ago = datetime.now() - timedelta(days=365)
        self.binance_client = BinanceClient(
            os.getenv("API_KEY"), os.getenv("API_SECRET")
        )
        self.dominance_data = get_binance_dominance_data()
        self.yahoo_data = YahooMarketReader(one_year_ago, datetime.now()).get_data()
        self.fear_greed_data = FearGreedIndexReader(one_year_ago).get_data()

    def predict(self, symbol: Symbols, start_time: datetime, interval: Intervals):
        data = self.prepare_X(symbol, start_time, interval)
        return self.models[symbol].predict(data)

    def prepare_X(self, symbol: Symbols, date_time: datetime, interval: Intervals):

        df = get_candles_from_binance(
            symbol, interval, None, date_time, self.limit_by_interval[interval]
        )
        df = df.merge(self.fear_greed_data, on="close_time_day", how="left")
        df = df.merge(self.dominance_data, on="close_time_day", how="left")
        df = df.merge(self.yahoo_data, on="close_time_day", how="left")

        df = add_metrics(df)
        df = clean_data(df)
        df = add_target(df)

        pipeline = create_pipeline(df)
        df = pd.DataFrame(
            pipeline.fit_transform(df),
            columns=pipeline.get_feature_names_out(),
        )

        return pad_sequences([df], dtype="float32", value=-999, maxlen=168)


if __name__ == "__main__":
    from dotenv import load_dotenv, find_dotenv

    # Uncomment next line in case that you create and execute any main function inside this folder.
    load_dotenv(find_dotenv())

    res = CryptoPredictor().predict(Symbols.ETHUSDT, datetime.now(), Intervals.ONE_HOUR)
    print(res)
