import websocket
import requests
import json
import datetime
import redis
from decimal import Decimal, ROUND_DOWN
from interval_trigger.pubsub.pub import Publisher

# 중요한 값은 상수사용합니다.
SYMBOL_LIST_ENDPOINT = "https://www.okex.com/api/v5/market/tickers?instType=SWAP"
# ENDPOINT = "wss://ws.bitmex.com/realtime"
ENDPOINT = "wss://ws.okx.com:8443/ws/v5/public"
rd = redis.StrictRedis(host='localhost', port=6379, db=0)


def is_calculation_open_close_interval(data1, data2, item_key):
    open_price = Decimal(str(data1['last']))
    close_price = Decimal(str(data2['last']))
    gap_price = open_price - close_price
    interval_price = ((gap_price / open_price) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
    if 'trigger' in data2:
        if data2['trigger'] == 'false':
            if interval_price > Decimal('3'):
                data2['trigger'] = 'true'
                data1['interval'] = str(interval_price)
                data1['exchange'] = "okx"
                data1['mode'] = "swap"
                Publisher().publish('channel', json.dumps(data1))
                print('발동 : ', data1)
                print('간격 : ', interval_price)
                rd.set(item_key, json.dumps(data2))
            elif interval_price < Decimal('-5'):
                data2['trigger'] = 'true'
                data1['interval'] = str(interval_price)
                data1['exchange'] = "okx"
                data1['mode'] = "swap"
                Publisher().publish('channel', json.dumps(data1))
                print("마이너스 : ", data1)
                print('간격 : ', interval_price)
                rd.set(item_key, json.dumps(data2))
            else:
                pass
        else:
            pass  # print(gap_price)


def sendRequest(url):
    """
    마켓 리스트 생성
    USDT 시장만 추출
    :param url: 티커리스트 url
    :return: 마켓리스트
    """
    markets = requests.get(url).json()
    marekt_list = []
    if 'data' in markets:
        data = markets['data']
        for i in data:
            marekt_list.append(i['instId'])
    print(marekt_list)
    return marekt_list


def getBitmexSymbolList(contents):
    """
    subscribe 생성
    :param contents: 마켓리스트
    :return:
    """
    format_list = []
    for i in contents:
        data = {"channel": "tickers",
                 "instType": "SWAP",
                 "instId": i}
        format_list.append(data)
    return {"op": "subscribe", "args": format_list}


def on_message(ws, message):
    my_dict = json.loads(message)
    if 'data' in my_dict:
        symbol = my_dict['data'][0]['instId']
        item_key = 'okx:' + symbol
        json_data = my_dict['data'][0]
        data_ttm = datetime.datetime.fromtimestamp(int(my_dict['data'][0]['ts']) / 1000)
        data_time = int(int(data_ttm.minute) / 5)
        data = rd.get(item_key)
        if data is not None:
            data2 = json.loads(data.decode())
            getdata_ttm = datetime.datetime.fromtimestamp(int(data2['ts']) / 1000)
            getdata_time = int(int(getdata_ttm.minute) / 5)
            if data_time == getdata_time:
                is_calculation_open_close_interval(json_data, data2, item_key)
            else:
                json_data['trigger'] = 'false'
                rd.set(item_key, json.dumps(json_data))
        else:
            json_data['trigger'] = 'false'
            rd.set(item_key, json.dumps(json_data))

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
    ws.close()

def on_open(ws):
    print("### open ###")
    contents = sendRequest(SYMBOL_LIST_ENDPOINT)
    symbols = getBitmexSymbolList(contents)
    ws.send(json.dumps(symbols))


def run(endpoint):
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(endpoint,
                                on_open = on_open,
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close,
                                on_ping=on_ping,
                                on_pong=on_pong)

    ws.run_forever(ping_interval=60, ping_timeout=10,ping_payload='PING')

if __name__ == "__main__":
    run(ENDPOINT)
    # sendRequest(SYMBOL_LIST_ENDPOINT)
