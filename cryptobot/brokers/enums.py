from enum import Enum

class Symbols(Enum):
    BTCUSDT = 'BTCUSDT'
    
class Intervals(Enum):
    ONE_HOUR = '1h'
    EIGHT_HOURS = '8h'
    
class OperationType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'
    
class SnapshotType(Enum):
    SPOT = 'SPOT'
    MARGIN = 'MARGIN'
    FUTURES = 'FUTURES'
    
class OrderType(Enum):
    MARKET = 'MARKET'