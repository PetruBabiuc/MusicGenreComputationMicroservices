import time
from threading import Thread

from src.helpers.SynchronizedDict import SynchronizedDict


def test1():
    elements_to_add = 10000
    threads_number = 100

    def add_in_dict(_dict, i):
        _dict[i] = []
        for ii in range(elements_to_add):
            with _dict:
                _dict[i].append(ii)

    d = SynchronizedDict()
    threads = [Thread(target=add_in_dict, args=(d, i)) for i in range(threads_number)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for i in range(threads_number):
        for j in range(elements_to_add):
            if d[i][j] != j:
                print(f'Error: in thread {i}, element on index {j} was {d[i][j]}, not {j}')
                return
    print('OK!')
    pass


def test2():
    elements_to_add = 10000
    threads_number = 100

    def add_in_dict(_dict, i):
        _dict[i] = []
        for ii in range(elements_to_add):
            _dict[i].append(ii)

    d = {}
    threads = [Thread(target=add_in_dict, args=(d, i)) for i in range(threads_number)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    for i in range(threads_number):
        for j in range(elements_to_add):
            if d[i][j] != j:
                print(f'Error: in thread {i}, element on index {j} was {d[i][j]}, not {j}')
                return
    print('OK!')
    pass


def test3():
    def thread_target(d):
        with d:
            time.sleep(1)

    sync_dict = SynchronizedDict()
    threads = [Thread(target=thread_target, args=(sync_dict,)) for _ in range(1000)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()


def test4():
    d = {'Pop': 10, 'Rock': 15, 'Electronic': 9}
    genre, count = max(d.items(), key=lambda it: it[1])
    pass


if __name__ == '__main__':
    test3()
