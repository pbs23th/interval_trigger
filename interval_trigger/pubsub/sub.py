import json
from interval_trigger.logset import loggers
import redis
from interval_trigger.slack.send_massage import send_message

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
        loggers().info(str(data))
        send_message(send_data)

    def phase_data(self, data):
        if data['exchange'] == 'upbit':
            respone_data = {
                'exchange': data['exchange'],
                'mode': data['mode'],
                'market': data['cd'],
                'interval': data['interval'],
                'price': data['tp'],
            }
            return respone_data
        elif data['exchange'] == 'okx':
            respone_data = {
                'exchange': data['exchange'],
                'mode': data['mode'],
                'market': data['instId'],
                'interval': data['interval'],
                'price': data['last'],
            }
            return respone_data

if __name__ == '__main__':
    Subscriber().listen('channel')
