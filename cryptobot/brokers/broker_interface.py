from abc import abstractmethod, ABCMeta

from cryptobot.brokers.enums import Symbols, Intervals

"""
This interface defines all the methods that all broker connectors must implement.
"""

class BrokerInterface:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def __init__(self, api_key, secret_key):
        pass
    
    @abstractmethod
    def get_account_status(self) -> dict:
        pass
    
    @abstractmethod
    def create_sell_order(self, symbol: Symbols, quantity: float):
        pass
    
    @abstractmethod
    def create_buy_order(self, symbol: Symbols, quantity: float):
        pass
    
    @abstractmethod
    def get_last_complete_candle(self, symbol: Symbols, interval: Intervals) -> dict:
        pass
    
    @abstractmethod
    def get_current_candle(self, symbol: str, interval: Intervals) -> dict:
        pass
