import json
import redis
import os
import asyncio
import httpx
from interval_trigger.slack.send_massage import send_message as slack_message

async def send_api(data):
    url = "http://13.209.224.209:5000/bots/api/signal"
    timeout = httpx.Timeout(connect=None, read=None, write=None, pool=None)
    async with httpx.AsyncClient(timeout=timeout) as client:
        res = await client.post(url, json=data)

class Subscriber:
    def __init__(self):
        self.redis = redis.Redis()
        self.pubsub = self.redis.pubsub()

    def subscribe(self, channel):
        self.pubsub.subscribe(channel)

    def listen(self, channel):
        self.subscribe(channel)
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                data = message['data'].decode()
                self.send_message(data)

    def send_message(self, data):
        print(f"send_slack - {data}")
        send_data = self.phase_data(json.loads(data))
        print(f"send_slack_send_data - {send_data}")
        slack_message(send_data)
        asyncio.run(send_api(send_data))

    def phase_data(self, data):
        if data['exchange'] == 'upbit':
            respone_data = {
                'exchange': data['exchange'],
                'mode': data['mode'],
                'market': data['cd'],
                'signal_interval': data['interval'],
                'price': data['tp'],
            }
            return respone_data
        elif data['exchange'] == 'okx':
            respone_data = {
                'exchange': data['exchange'],
                'mode': data['mode'],
                'market': data['instId'],
                'signal_interval': data['interval'],
                'price': data['last'],
                'vol24h': data['volCcy24h'],
                'vol': data['vol'],
            }
            return respone_data

if __name__ == '__main__':
    Subscriber().listen('channel')
