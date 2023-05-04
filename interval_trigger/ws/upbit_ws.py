import websocket
import requests
import json
from datetime import datetime
import redis
from decimal import Decimal
from interval_trigger.pubsub.pub import Publisher
# 중요한 값은 상수사용합니다.
SYMBOL_LIST_ENDPOINT = "https://api.upbit.com/v1/market/all"
# ENDPOINT = "wss://ws.bitmex.com/realtime"
ENDPOINT = "wss://api.upbit.com/websocket/v1"
rd = redis.StrictRedis(host='localhost', port=6379, db=0)
r = redis.Redis()
first_data = {}


def is_calculation_open_close_interval(data1, data2, item_key):
    open_price = Decimal(str(data1['tp']))
    close_price = Decimal(str(data2['tp']))
    gap_price = open_price - close_price
    interval_price = (gap_price / open_price) * Decimal('100')
    if 'trigger' in data2:
        if data2['trigger'] == 'false':
            if interval_price > Decimal('3'):
                data2['trigger'] = 'true'
                data1['interval'] = str(interval_price)
                data1['exchange'] = "upbit"
                data1['mode'] = "spot"
                Publisher().publish('channel', json.dumps(data1))
                print('발동 : ', data1)
                print('간격 : ', interval_price)
                rd.set(item_key, json.dumps(data2))
            # elif interval_price < Decimal('-5'):
            #     data2['trigger'] = 'true'
            #     data1['interval'] = str(interval_price)
            #     data1['exchange'] = "upbit"
            #     data1['mode'] = "spot"
            #     Publisher().publish('channel', json.dumps(data1))
            #     print("마이너스 : ", data1)
            #     print('간격 : ', interval_price)
            #     rd.set(item_key, json.dumps(data2))
            else:
                pass
        else:
            pass  # print(gap_price)


def sendRequest(url):
    markets = requests.get(url).json()
    market_data = []
    for market in markets:
        if market['market'][:3] == "KRW":
            if market['market'] != "KRW-BTT":
                market_data.append(market['market'])
    return market_data


def getBitmexSymbolList(contents):
    return [{"ticket": "test"}, {"type": "trade", "codes": contents}, {"format": "SIMPLE"}]


def on_message(ws, message):
    my_dict = json.loads(message)
    # print(my_dict)
    ttm = my_dict['ttm'].split(':')[1]
    data_time = int(int(ttm) / 5)
    # ws.close(status=websocket.STATUS_PROTOCOL_ERROR)
    if 'ty' in my_dict:
        code = my_dict['cd']
        item_key = 'upbit:' + code
        data = rd.get(item_key)
        if data is not None:
            data2 = json.loads(data.decode())
            getdata_ttm = data2['ttm'].split(':')[1]
            getdata_time = int(int(getdata_ttm) / 5)
            if data_time == getdata_time:
                is_calculation_open_close_interval(my_dict, data2, item_key)
            else:
                my_dict['trigger'] = 'false'
                rd.set(item_key, json.dumps(my_dict))
        else:
            my_dict['trigger'] = 'false'
            rd.set(item_key, json.dumps(
                my_dict))


def on_ping(ws, message):
    print("Got a ping! A pong reply has already been automatically sent.")
    print(message)


def on_pong(ws, message):
    print("Got a pong! No need to respond")
    print(message)


def on_error(ws, error):
    print(error)
    ws.on_close(ws)


def on_close(ws):
    print("### closed ###")
    print(datetime.now())
    ws.close()


def on_open(ws):
    print("### open ###")
    contents = sendRequest(SYMBOL_LIST_ENDPOINT)
    symbols = getBitmexSymbolList(contents)
    print(symbols)
    ws.send(json.dumps(symbols))


def run(endpoint):
    # websocket.enableTrace(False)
    ws = websocket.WebSocketApp(endpoint, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close,
                                on_ping=on_ping, on_pong=on_pong)

    ws.run_forever(ping_interval=60, ping_timeout=10, ping_payload='PING')


if __name__ == "__main__":
    run(ENDPOINT)  # sendRequest(SYMBOL_LIST_ENDPOINT)  # print(28049966 % 5)
