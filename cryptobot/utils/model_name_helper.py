import os

from cryptobot.brokers.enums import Symbols

GCM_BUCKET = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")
PATH_FORMAT = "gs://{bucket}/trained_models/{symbol}/{version}/model"


def generate_latest_model_path(symbol: Symbols):
    return PATH_FORMAT.format(bucket=GCM_BUCKET, symbol=symbol.value, version="latest")
