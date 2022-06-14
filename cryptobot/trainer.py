from datetime import datetime
import logging
import os

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder, RobustScaler
from cryptobot.utils.pipeline_helper import create_pipeline
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras import Sequential, layers
from tensorflow.keras.layers.experimental.preprocessing import Normalization
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.models import save_model


from cryptobot.brokers.enums import Intervals, Symbols
from cryptobot.data import (
    add_target,
    clean_data,
    get_data,
)
from cryptobot.utils.feature_engineering import add_metrics
from cryptobot.utils.data_train_split_helper import get_X_y, split_train_test_data


class Trainer(object):
    def __init__(
        self,
        symbol: Symbols,
        interval: Intervals,
        start_time: datetime,
        end_time: datetime,
        **kwargs,
    ):
        self.symbol = symbol
        self.interval = interval
        self.start_time = start_time
        self.end_time = end_time

        self.kwargs = kwargs
        self.local = kwargs.get("local", True)

    def preprocess_data(self):
        self.data = get_data(self.symbol, self.interval, self.start_time, self.end_time)
        self.data = add_metrics(self.data)
        self.data = clean_data(self.data)
        self.data = add_target(self.data)

        self.set_pipeline()
        self.preprocessed_data = pd.DataFrame(
            self.pipeline.fit_transform(self.data),
            columns=self.pipeline.get_feature_names_out(),
        )
        return self.preprocessed_data

    def set_pipeline(self):
        """
        Creates the pipeline for the model.
        """
        self.pipeline = create_pipeline(self.data)

    def set_model(self):
        normalizer = Normalization()
        normalizer.adapt(self.X_train_pad)
        self.model = Sequential()
        self.model.add(normalizer)
        self.model.add(layers.Masking(mask_value=-1))
        self.model.add(layers.LSTM(30, activation="tanh", return_sequences=True))
        self.model.add(layers.LSTM(20, activation="tanh"))
        self.model.add(layers.Dense(20, activation="tanh"))
        self.model.add(layers.Dropout(0.2))
        self.model.add(layers.Dense(20, activation="tanh"))
        self.model.add(layers.Dropout(0.2))
        self.model.add(layers.Dense(1, activation="sigmoid"))
        return self.model

    def split_data(self):

        df_train, df_test = split_train_test_data(self.preprocessed_data)

        length_of_observations = np.random.randint(120, 168, 10000)
        X_train, y_train = get_X_y(df_train, length_of_observations)
        self.X_train = X_train
        self.y_train = y_train

        length_of_observations = np.random.randint(120, 168, 1000)
        X_test, y_test = get_X_y(df_test, length_of_observations)
        self.X_test = X_test
        self.y_test = y_test

        self.X_train_pad = pad_sequences(self.X_train, dtype="float32", value=-999)

    def train_model(self):

        logging.info(f"Starting training for {self.symbol.value}")

        self.model.compile(
            loss="binary_crossentropy",
            optimizer=RMSprop(learning_rate=0.05),
            metrics="accuracy",
        )

        self.model.fit(
            self.X_train_pad,
            np.array(self.y_train),
            epochs=50,
            callbacks=[EarlyStopping(patience=5)],
            batch_size=128,
            validation_split=0.3,
        )

    def save_model(self):
        bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
        version = datetime.now().strftime("%Y%m%d-%H%M%S")
        latest_path = f"gs://{bucket}/trained_models/{self.symbol.value}/latest/model"
        version_path = (
            f"gs://{bucket}/trained_models/{self.symbol.value}/{version}/model"
        )

        logging.info(f"Saving model to {version_path}")
        save_model(self.model, version_path, overwrite=True, save_format="tf")
        save_model(self.model, latest_path, overwrite=True, save_format="tf")


if __name__ == "__main__":

    symbol = Symbols.ETHUSDT
    interval = Intervals.ONE_HOUR
    start_time = datetime(2018, 2, 1)
    end_time = datetime(2022, 5, 31)

    trainer = Trainer(symbol, interval, start_time, end_time)
    res = trainer.preprocess_data()
    trainer.split_data()
    trainer.set_model()
    trainer.train_model()
    trainer.save_model()
