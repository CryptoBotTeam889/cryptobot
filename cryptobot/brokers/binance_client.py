from datetime import datetime
from http import HTTPStatus
from binance import Client

from cryptobot.brokers.broker_interface import BrokerInterface
from cryptobot.brokers.enums import OrderType, SnapshotType, Symbols, Intervals, OperationType

COLUMNS = ['open_time', 'open', 'high', 'low', 'close',
                'volume', 'close_time', 'quote_asset_volume',
                'number_of_trades', 'taker_buy_base_asset_volume',
                'taker_buy_quote_asset_volume']

class BinanceClient(BrokerInterface):
    """
    A class that handles one connection to the Binance API for one account.
    It means that if you have multiple accounts, you need to have multiple BinanceClient instances.
    It offers a bunch of methods to interact with the Binance API easily and abstract unnecessary complexities.
    
    Attributes
    ----------
    client : BinanceClient
        It's the connection to the Binance API.
        
    Instance methods
    -------
    get_account_status()
        Returns the status of the account. It includes the balances of the distint currencies.
    
    get_current_candle(symbol: Symbols, interval: Intervals)
        Returns the current candle of the given symbol and interval.
    
    get_last_complete_candle(symbol: Symbols, interval: Intervals)
        Returns the last complete candle for the given symbol and interval.
        
    create_buy_order(symbol: Symbols, quantity: float)
        Create a buy order for the given symbol and quantity, considering the market price.
    
    create_sell_order(symbol: Symbols, quantity: float)
        Create a sell order for the given symbol and quantity, considering the market price.
        
    """
    
    def __init__(self, api_key, secret_key):
        """
        Parameters
        ----------
        api_key : str
            It's the API key of the account.
            
        secret_key : str
            It's the secret key of the account.
        """
        
        self.client = Client(api_key, secret_key, testnet=True)
    
    def get_account_status(self):
        """
        Returns the status of the account. It includes the balances of the distinct currencies.

        Returns
        -------
        dict
            Contains the balances of the account. Each balance is a dict with the asset, free and locked.
            Also contains the totalAssetOfBtc key, which is the total asset of the account in BTC.
            Example: 
                {
                    'totalAssetOfBtc': '0.00066998',
                    'balances': [
                        {'asset': 'ETH', 'free': '0.0115', 'locked': '0'}
                    ]
                }
                
        Raises
        ------
        Exception
            If the response status is not 200, or there's more than one snapshot vos in Binance account snapshot.
        """
        
        res = self.client.get_account_snapshot(type=SnapshotType.SPOT.value)
        if res.get('code') != HTTPStatus.OK:
            raise Exception('Error while getting account status. {}'.format(res.get('msg')))
        return parse_account_snapshot(res)
    
    def get_current_candle(self, symbol: Symbols, interval: Intervals):
        """
        Returns the current candle of the given symbol and interval.
        By current, it means that the candle is not complete, so the close time is after the current time.
        
        See docstring of :Symbols:`cryptobot.brokers.enums.Symbols` for more info about the symbols.
        See docstring of :Intervals:`cryptobot.brokers.enums.Intervals` for more info about the intervals.
        
        Parameters
        ----------
        symbol : Symbols
            It's the symbol of the candle.
        
        Inteval: Intervals
            It's the interval of the candle.
            
        Returns
        -------
        list
            The list includes the values of the candle in the next order:
                open_time, open, high, low, close,
                volume, close_time, quote_asset_volume,
                number_of_trades, taker_buy_base_asset_volume,
                taker_buy_quote_asset_volume, ignore.

            Example: [1654686000000, 30382.79, 30504.86, 30340.73, 30419.64,
                        217.160362, 1654689599999, 6608879.303886, 6047, 125.007039, 3804377.38752454]
        
        Raises
        ------
        Exception
            If the Binance API returns no candles.
        """
        
        candles = self.client.get_klines(symbol=symbol.value, interval=interval.value, limit=1)
        if candles:
            return parse_candle(candles[0])
        raise Exception('Binance API didn\'t return any candle for symbol: {} and interval: {}. '.format(symbol.value, interval.value))
    
    def get_last_complete_candle(self, symbol: Symbols, interval: Intervals):
        """
        Returns the last complete candle for the given symbol and interval.
        It means that the candle is complete, so the close time is before the current time. 
        
        See docstring of :Symbols:`cryptobot.brokers.enums.Symbols` for more info about the symbols.
        See docstring of :Intervals:`cryptobot.brokers.enums.Intervals` for more info about the intervals.
        
        Parameters
        ----------
        symbol : Symbols
            It's the symbol of the candle.
        
        interval : Intervals
            It's the interval of the candle.
            
        Returns
        -------
        list
            The list includes the values of the candle in the next order:
                open_time, open, high, low, close,
                volume, close_time, quote_asset_volume,
                number_of_trades, taker_buy_base_asset_volume,
                taker_buy_quote_asset_volume, ignore.

            Example: [1654686000000, 30382.79, 30504.86, 30340.73, 30419.64,
                        217.160362, 1654689599999, 6608879.303886, 6047, 125.007039, 3804377.38752454]
        
        Raises
        ------
        Exception
            If the Binance API returns no candles.
        """
 
        candles = self.client.get_klines(symbol=symbol.value, interval=interval.value, limit=2)
        if candles:
            return parse_candle(candles[0])
        raise Exception('Binance API didn\'t return any candle for symbol: {} and interval: {}. '.format(symbol.value, interval.value))
    
    def get_candles(self, symbol: Symbols, interval: Intervals, start_time: datetime, end_time: datetime):
        """
        Returns the last complete candle for the given symbol and interval.
        It means that the candle is complete, so the close time is before the current time. 
        
        See docstring of :Symbols:`cryptobot.brokers.enums.Symbols` for more info about the symbols.
        See docstring of :Intervals:`cryptobot.brokers.enums.Intervals` for more info about the intervals.
        
        Parameters
        ----------
        symbol : Symbols
            It's the symbol of the candle.
        
        inteval : Intervals
            It's the interval of the candle.
        
        start_time : datetime
            It's the open time of the first candle.
        
        end_time : datetime
            It's the close time of the last candle.
                    
        Returns
        -------
        list
            The list contains lists that include the values of the candle in the same order
            that COLUMNS constant.

            Example: [[1654686000000, 30382.79, 30504.86, 30340.73, 30419.64,
                        217.160362, 1654689599999, 6608879.303886, 6047, 125.007039, 3804377.38752454]]
        """
        
        start = round(start_time.timestamp()) * 1000
        end = round(min(end_time.timestamp(), datetime.now().timestamp())) * 1000
        candles = []
        while(start < end):
            candles_aux = self.client.get_klines(symbol=symbol.value, interval=interval.value, startTime = start, endTime = end, limit=1000)
            candles = candles + candles_aux
            start = candles_aux[-1][6] if candles_aux else end
            
        return [parse_candle(candle) for candle in candles]

    def create_buy_order(self, symbol: Symbols, quantity: float):
        """
        Create a buy order for the given symbol and quantity, considering the market price.
        For example, if the symbol is BTCUSDT, it will buy as many BTC as quantity USDT can.
        
        See docstring of :Symbols:`cryptobot.brokers.enums.Symbols` for more info about the symbols.
        See docstring of :Intervals:`cryptobot.brokers.enums.Intervals` for more info about the intervals.
        
        Parameters
        ----------
        symbol : Symbols
            It's the symbol of the candle.
        
        quantity : float
            Assuming the symbol XY, it's the amount of Y to spend to buy X.

        """
        return self.client.create_test_order(symbol = symbol.value, side = OperationType.BUY.value, type = OrderType.MARKET.value, quoteOrderQty = quantity)
        
    def create_sell_order(self, symbol: Symbols, quantity: float):
        """
        Create a sell order for the given symbol and quantity, considering the market price.
        For example, if the symbol is BTCUSDT, it will sell the quantity of BTC and will get USDT.
        
        See docstring of :Symbols:`cryptobot.brokers.enums.Symbols` for more info about the symbols.
        See docstring of :Intervals:`cryptobot.brokers.enums.Intervals` for more info about the intervals.
        
        Parameters
        ----------
        symbol : Symbols
            It's the symbol of the candle.
        
        quantity : float
            Assuming the symbol XY, it's the amount of Y to spend to buy X.

        """
        return self.client.create_test_order(symbol = symbol.value, side = OperationType.SELL.value, type = OrderType.MARKET.value, quantity = quantity)  
    
    
def parse_account_snapshot(snapshot):
    vos = snapshot.get('snapshotVos')
    if len(vos) != 1:
        raise Exception('There should be only one snapshot vos in Binance account snapshot.')
    data = vos[0].get('data')
    return {
        'totalAssetOfBtc': float(data.get('totalAssetOfBtc')),
        'balances': [{'asset': balance.get('asset'), 'free': float(balance.get('free')), 'locked': float(balance.get('locked'))} for balance in data.get('balances')]
    }

def parse_candle(candle):
    """Cast values to float and remove unused fields"""
    return [
        candle[0],
        float(candle[1]),
        float(candle[2]),
        float(candle[3]),
        float(candle[4]),
        float(candle[5]),
        candle[6],
        float(candle[7]),
        candle[8],
        float(candle[9]),
        float(candle[10])
    ]
