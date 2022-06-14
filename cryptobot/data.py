import logging
import os
from datetime import datetime

import pandas as pd
from cryptobot.brokers.binance_client import BinanceClient
from cryptobot.brokers.enums import Intervals, Symbols
from cryptobot.readers.fear_greed_index_reader import FearGreedIndexReader
from cryptobot.readers.yahoo_market_reader import YahooMarketReader

binance_client = BinanceClient(os.getenv("API_KEY"), os.getenv("API_SECRET"))

BUCKET = f"gs://{os.getenv('GOOGLE_CLOUD_STORAGE_BUCKET')}/raw_data"


def get_data(symbol: Symbols, interval: str, start_time: datetime, end_time: datetime):
    logging.info(
        f"Start getting data for symbol: {symbol.value}, candle duration: {interval.value}, start_time: {start_time}, end_time: {end_time}"
    )
    df = get_candles_from_binance(symbol, interval, start_time, end_time)
    df_aux = FearGreedIndexReader(start_time).get_data()  # TODO use singleton
    df = df.merge(df_aux, on="close_time_day", how="left")
    df_aux = get_binance_dominance_data()
    df = df.merge(df_aux, on="close_time_day", how="left")
    df_aux = YahooMarketReader(start_time, end_time).get_data()
    df = df.merge(df_aux, on="close_time_day", how="left")
    return df


def interpolate_data(df):
    not_fillna = [
        "open_time",
        "close_time",
        "close_time_min",
        "close_time_day",
    ]
    aux_df = df.drop(columns=not_fillna)
    aux_df.interpolate(method="linear", limit_direction="forward", axis=0, inplace=True)
    df[list(aux_df.columns)] = aux_df
    return df


def clean_data(df):
    df = interpolate_data(df)
    df["FG_val_clasif"] = df["FG_val_clasif"].fillna(method="ffill")
    # df["FG_value"] = df["FG_value"].fillna(method="ffill")
    columns_to_drop = ["open_time", "close_time", "close_time_min", "close_time_day"]
    df.drop(columns=columns_to_drop, inplace=True)
    df = df[200:]
    return df


def add_target(df):
    df["target"] = (df.close - df.open).apply(lambda x: 0 if x < 0 else 1)
    return df


def get_candles_from_binance(
    symbol: Symbols,
    interval: str,
    start_time: datetime,
    end_time: datetime,
    limit: int = None,
):
    logging.info(f"Getting data from Binance API")

    df = pd.DataFrame(
        binance_client.get_candles(symbol, interval, start_time, end_time, limit),
        columns=BinanceClient.COLUMNS_CANDLE,
    )

    return parse_candles_data(df)


def parse_candles_data(df):

    df["open_time"] = df["open_time"].apply(
        lambda x: datetime.utcfromtimestamp(x / 1e3)
    )
    df["close_time"] = df["close_time"].apply(
        lambda x: datetime.utcfromtimestamp(x / 1e3)
    )
    df["close_time_min"] = df["close_time"].apply(
        lambda x: x.strftime("%Y-%m-%d-%H-%M")
    )
    df["close_time_day"] = df["close_time"].apply(lambda x: x.strftime("%Y-%m-%d"))
    df = df.drop(
        columns=[
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
        ]
    )
    return df


def get_binance_dominance_data():
    logging.info(f"Getting data about Binance Dominance from {BUCKET}")
    path = f"{BUCKET}/BTC Dominance - Trading View - 1day.csv"
    df = read_data_from_gs(path)
    df["time"] = df["time"].apply(lambda x: datetime.utcfromtimestamp(int(x)))
    df["close_time_day"] = df["time"].apply(lambda x: x.strftime("%Y-%m-%d"))
    df["btc_avg"] = df["open"] + df["close"] + df["high"] + df["low"] / 4
    df.drop(
        columns=["time", "open", "high", "low", "close", "Volume", "Volume MA"],
        inplace=True,
    )
    return df


def read_data_from_gs(path):
    df = pd.read_csv(path)
    return df


if __name__ == "__main__":
    symbol = Symbols.ETHUSDT
    interval = Intervals.ONE_HOUR
    start_time = datetime(2018, 2, 1)
    end_time = datetime(2022, 5, 31)
    get_data(symbol, interval, start_time, end_time)
