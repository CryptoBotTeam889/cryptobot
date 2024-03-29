from enum import Enum


class Symbols(Enum):
    BTCUSDT = "BTCUSDT"
    ETHUSDT = "ETHUSDT"


class Intervals(Enum):
    ONE_HOUR = "1h"
    EIGHT_HOURS = "8h"
    ONE_DAY = "1d"


class OperationType(Enum):
    BUY = "BUY"
    SELL = "SELL"


class SnapshotType(Enum):
    SPOT = "SPOT"
    MARGIN = "MARGIN"
    FUTURES = "FUTURES"


class OrderType(Enum):
    MARKET = "MARKET"
