import json
import threading
import time

import redis


def line_generator(n: int):
    for i in range(n):
        yield f'Line {i}'


def item_generator(n: int):
    for i in range(n):
        yield json.dumps({'item': i})


def create_redis():
    return redis.StrictRedis('localhost', 6379, encoding='utf-8', decode_responses=True)


def publish():
    red = create_redis()
    lines = line_generator(10)
    for line in lines:
        red.publish('c1', line[:2])
        time.sleep(1)
        red.publish('c2', line)
        time.sleep(1)


def listen(topic: str):
    red = create_redis()
    sub = red.pubsub()
    sub.subscribe(topic)
    for message in sub.listen():
        print(f'[{threading.current_thread().getName()}] Topic: {topic}: {message}')


def publish2():
    red = create_redis()
    lines = item_generator(10)
    for line in lines:
        red.publish('c1', line.encode())
        time.sleep(1)


def listen2(topic: str):
    red = create_redis()
    sub = red.pubsub(ignore_subscribe_messages=True)
    sub.subscribe(topic)
    # sub.subscribe(topic)
    for message in sub.listen():
        message = message['data']
        message = json.loads(message)
        if message['item'] == 3:
            # sub.reset()
            time.sleep(3)
            sub.subscribe(topic)
        print(f'[{threading.current_thread().getName()}] Topic: {topic}: {message}')


def test1():
    threads = [
        threading.Thread(target=publish),
        # threading.Thread(target=listen, args=('c1',), name='THREAD c1'),
        # threading.Thread(target=listen, args=('c1',), name='THREAD c1'),
        # threading.Thread(target=listen, args=('c1',), name='THREAD c1'),
        # threading.Thread(target=listen, args=('c2',), name='THREAD c2')
    ]
    for t in threads:
        t.start()
        time.sleep(0.25)
    for t in threads:
        t.join()


def test2():
    threads = [
        threading.Thread(target=publish2),
        threading.Thread(target=listen2, args=('c1',), name='THREAD c1'),
    ]
    for t in threads:
        t.start()
        time.sleep(0.25)
    for t in threads:
        t.join()


def test_docker_redis():
    r = create_redis()

    r.ping()

    print('Connected to redis...')


if __name__ == '__main__':
    test_docker_redis()
