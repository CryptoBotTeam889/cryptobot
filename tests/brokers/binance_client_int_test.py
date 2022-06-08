import os
import pytest

from cryptobot.brokers.binance_client import BinanceClient, parse_account_snapshot, parse_candle
from cryptobot.brokers.enums import Intervals, Symbols

@pytest.fixture
def binance_client():
    print("SECRETS", os.getenv('API_KEY'), os.getenv('API_SECRET'))
    return BinanceClient(os.getenv('API_KEY'), os.getenv('API_SECRET'))

@pytest.fixture
def interval():
    # In case of changing this interval, please change the fixture below.
    return Intervals.ONE_HOUR

@pytest.fixture
def interval_in_timestamp():
    return to_timestamp(hours = 1)

@pytest.mark.skip(reason = "We need a real account for this test.")
def test_account_status_response_format(binance_client):
    status = binance_client.get_account_status()
    assert all(k in ["totalAssetOfBtc", "balances"] for k in status.keys())
    assert type(status.get("balances")) == list
    assert all(k in ["asset", "free", "locked"] for k in status.get("balances")[0].keys())
    assert len(status.get("balances")[0].keys()) == 3
    
def test_get_current_candle_response_format(binance_client, interval, interval_in_timestamp):
    current_candle = binance_client.get_current_candle(Symbols.BTCUSDT, interval)
    assert type(current_candle) == list
    assert len(current_candle) == 11
    assert current_candle[6] - current_candle[0] < interval_in_timestamp

def test_get_last_complete_candle_response_format(binance_client, interval, interval_in_timestamp):
    current_candle = binance_client.get_last_complete_candle(Symbols.BTCUSDT, interval)
    assert type(current_candle) == list
    assert len(current_candle) == 11
    assert current_candle[6] - current_candle[0] + 1 == interval_in_timestamp
  
def test_create_buy_order(binance_client):
    # For now, we only check it doesn't blow up.
    # TODO Improve this test.
    binance_client.create_buy_order(Symbols.BTCUSDT, 10)

def test_create_sell_order(binance_client):
    # For now, we only check it doesn't blow up.
    # TODO Improve this test.__
    binance_client.create_sell_order(Symbols.BTCUSDT, 10)
    
def test_parse_candle():
    dirty_candle = [1654686000000, '30382.79000000', '30504.86000000', '30340.73000000', '30419.64000000',
                        '217.16036200', 1654689599999, '6608879.30388600', 6047, '125.00703900', '3804377.38752454', '0']
    expected_candle = [1654686000000, 30382.79, 30504.86, 30340.73, 30419.64,
                        217.160362, 1654689599999, 6608879.303886, 6047, 125.007039, 3804377.38752454]
    parsed_candle = parse_candle(dirty_candle)
    
    assert expected_candle == parsed_candle
    
def test_parse_account_snapshot():
    raw_snapshot = {'code': 200, 'msg': '', 'snapshotVos': [{'type': 'spot', 'updateTime': 1654646399000, 'data': {'totalAssetOfBtc': '0.00066998', 'balances': [{'asset': 'ETH', 'free': '0.0115', 'locked': '0'}]}}]}
    expected_parsed_snapshot = {'totalAssetOfBtc': 0.00066998, 'balances': [{'asset': 'ETH', 'free': 0.0115, 'locked': 0.0}]}
    parsed_snapshot = parse_account_snapshot(raw_snapshot)
    assert expected_parsed_snapshot == parsed_snapshot
    
def test_to_timestamp_util():
    assert to_timestamp(hours = 1) == 3600 * 1000
    assert to_timestamp(minutes = 1) == 60 * 1000
    assert to_timestamp(seconds = 1) == 1000
    assert to_timestamp(hours = 1, minutes = 1) == 3600 * 1000 + 60 * 1000
    assert to_timestamp(hours = 1, seconds = 1) == 3600 * 1000 + 1000
    assert to_timestamp(minutes = 1, seconds = 1) == 60 * 1000 + 1000
    assert to_timestamp(hours = 1, minutes = 1, seconds = 1) == 3600 * 1000 + 60 * 1000 + 1000

def to_timestamp(hours = 0, minutes = 0, seconds = 0):
    return (hours * 3600 + minutes * 60 + seconds) * 1000
