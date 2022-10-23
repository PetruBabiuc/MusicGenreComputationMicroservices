import json
import time
from collections import deque
from itertools import tee
from urllib.parse import urlparse, urljoin

import requests
import selenium.webdriver.firefox.webdriver
from lxml import etree
from pybloomfilter import BloomFilter
from selenium.webdriver.firefox.options import Options

from config.rabbit_mq import Crawler
from config.spider import BLOOM_FILTER_CAPACITY, BLOOM_FILTER_ERROR_RATE
from src.helpers import Base64Converter
from src.helpers.Mp3Spider import Mp3Spider
from src.helpers.RabbitMqConsumer import RabbitMqConsumer
from src.helpers.RabbitMqProducer import RabbitMqProducer
from src.model.SpiderReturn import SpiderReturn
from src.model.SpiderState import SpiderState


def test1():
    current_page = 'https://cdn.freesound.org/mtg-jamendo/raw_30s/audio/'
    domain = urlparse(current_page).netloc
    header = requests.head(current_page, allow_redirects=True)
    content_type = header.headers['Content-Type']
    if content_type == 'audio/mpeg':
        print(f'MP3 found: {current_page}')
        res = requests.get(current_page)
        song = res.content
        with open('downloaded_song.mp3', 'wb') as f:
            f.write(song)
        return
    res = requests.get(current_page)
    dom = etree.HTML(res.text)

    # Getting "a" elements that have "href" attribute
    elements = dom.xpath('//a[href]')

    # Extracting the "href" attribute
    found_urls = map(lambda it: it.attrib['href'], elements)

    # If the URL is relative, joining it to the domain. If it is absolute it will be left untouched.
    # (no matter if it has the same domain or not)
    found_urls = map(lambda it: urljoin(current_page, it), found_urls)

    # Filtering the domains that have the crawled domain
    found_urls = filter(lambda it: urlparse(it).netloc == domain, found_urls)

    # Cloning generator
    found_urls, found_music = tee(found_urls, 2)

    found_music = filter(lambda it: it.endswith('.mp3'), found_music)
    found_urls = filter(lambda it: not it.endswith('.mp3'), found_urls)
    found_urls = list(found_urls)
    found_music = list(found_music)

    pass


def test2():
    res = requests.get('https://freemusicarchive.org/track/revenge-from-behind-the-grave/download/')
    music = res.content
    with open('downloaded_music', 'wb') as f:
        f.write(music)
    pass


def test3():
    url = 'https://cdn.freesound.org/mtg-jamendo/raw_30s/audio/00/101000.mp3'
    driver_path = '/home/petru/Licenta/geckodriver'
    options = Options()
    options.headless = True
    options.add_argument('--window-size=1920x1080')
    options.add_argument('--incognito')
    driver = selenium.webdriver.Firefox(executable_path=driver_path, options=options)

    driver.get(url)
    time.sleep(2)
    pass


def test4():
    to_add = ['https://cdn.freesound.org/mtg-jamendo/raw_30s/audio/00/',
              'https://cdn.freesound.org/mtg-jamendo/raw_30s/audio/72/']
    to_check = [
        'https://cdn.freesound.org/mtg-jamendo/raw_30s/audio/raw_30s_audio-04.tar',
        'https://cdn.freesound.org/mtg-jamendo/'
    ]
    bloom_filter = BloomFilter(100000, 0.1, 'bloomfilter')
    for url in to_add:
        bloom_filter.add(url)
    serialized = bloom_filter.to_base64()
    deserialized = BloomFilter.from_base64('bloomfilter', serialized)
    for url in to_check + to_add:
        print(f'{url} -> {url in deserialized}')


def test6():
    with open('../../links.txt') as f:
        links = f.read().splitlines()
    for start_index, link in enumerate(links, 1):
        if link in links[start_index:]:
            print(f'Found duplicate: {link}')


def test7():
    domain = 'https://cdn.freesound.org/mtg-jamendo'
    max_items = 1
    max_resources = 0

    bloom_filter = BloomFilter(BLOOM_FILTER_CAPACITY, BLOOM_FILTER_ERROR_RATE, 'TestSpiderBloomFilter.raw')
    state = SpiderState(domain, bloom_filter, deque([domain]))
    mp3_spider = Mp3Spider(state, max_found_items=max_items, max_crawled_resources=max_resources)

    crawl_number = 1
    spider_return: SpiderReturn = SpiderReturn('', [''], [], 0, '')

    items_found = []
    resources_crawled = 0

    while spider_return.queue:
        print(f'{"@" * 10} Crawl {crawl_number} {"@" * 10}')
        spider_return = mp3_spider.crawl()
        items_found.extend(spider_return.urls_to_process)
        resources_crawled += spider_return.resources_crawled
        crawl_number += 1
        print()

    print(f'Resources crawled: {resources_crawled}\nItems found: {items_found}')
    pass


def test8():
    domain = 'https://cdn.freesound.org'
    queue = ['/mtg-jamendo']
    max_items = 2
    max_resources = 0

    bloom_filter_name = 'TestSpiderBloomFilter.raw'
    bloom_filter = BloomFilter(BLOOM_FILTER_CAPACITY, BLOOM_FILTER_ERROR_RATE, bloom_filter_name)
    state = SpiderState(domain, bloom_filter, deque(queue))
    mp3_spider = Mp3Spider(state, max_found_items=max_items, max_crawled_resources=max_resources)

    crawl_number = 1
    repeated_crawl = 2
    max_crawls = 3
    while crawl_number <= max_crawls:
        print(f'{"@" * 10} Crawl {crawl_number} {"@" * 10}')

        spider_return = mp3_spider.crawl()
        if crawl_number == repeated_crawl - 1:
            bloom_filter = BloomFilter.from_base64(bloom_filter_name, spider_return.bloom_filter)
            saved_state = SpiderState(
                domain, bloom_filter, deque(list(spider_return.queue))
            )
        crawl_number += 1
        print()

    print(f'Repeated crawl {repeated_crawl}:')
    mp3_spider.state = saved_state
    mp3_spider.crawl()


def test9():
    producer = RabbitMqProducer(Crawler.Spiders.RESTORE_STATE_QUEUE.exchange,
                                Crawler.Spiders.RESTORE_STATE_QUEUE.routing_key)

    def print_spider_return(message: bytes) -> None:
        deserialized_message = json.loads(message)

        for k, v in deserialized_message.items():
            print(f'{k} => {v}')
        print()
        if deserialized_message['queue']:
            producer.send_message(message)

    consumer = RabbitMqConsumer(Crawler.Spiders.RETURN_QUEUE.name, print_spider_return)

    state = {
        'client_id': 0,
        'domain': 'https://cdn.freesound.org',
        # 'queue': ['/mtg-jamendo']
    }
    state = json.dumps(state).encode()
    producer.send_message(state)
    consumer.start_receiving_messages()


def test10():
    genre = 'Rock'

    def print_url_processor_return(message: bytes) -> None:
        deserialized_message = json.loads(message)

        for k, v in deserialized_message.items():
            if k != 'song':
                print(f'{k} => {v}')

        if 'song' in deserialized_message:
            song = deserialized_message['song']
            song = Base64Converter.string_to_bytes(song)
            with open(f'{genre}.mp3', 'wb') as f:
                f.write(song)

    consumer = RabbitMqConsumer(Crawler.UrlProcessors.RETURN_QUEUE.name, print_url_processor_return)
    producer = RabbitMqProducer(Crawler.UrlProcessors.RESTORE_STATE_QUEUE.exchange,
                                Crawler.UrlProcessors.RESTORE_STATE_QUEUE.routing_key)
    state = {
        'client_id': 10,
        'domain': 'https://cdn.freesound.org/',
        'urls': ['mtg-jamendo/raw_30s/audio/00/1002000.mp3',  # Pop
                 'mtg-jamendo/raw_30s/audio/00/1007900.mp3',  # Rock
                 'mtg-jamendo/raw_30s/audio/00/1012600.mp3',  # Hip-Hop
                 ],
        'genre': genre
    }

    state = json.dumps(state).encode()
    producer.send_message(state)
    consumer.start_receiving_messages()


if __name__ == '__main__':
    test10()
