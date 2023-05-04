import redis

class Publisher:
    def __init__(self):
        self.redis = redis.Redis()

    def publish(self, channel, message):
        self.redis.publish(channel, message)


if __name__ == '__main__':
    Publisher().publish('channel', 'test')
