import time
import requests
from lxml import html
from pymongo import MongoClient
from fp.fp import FreeProxy
from fake_useragent import UserAgent
from random import randint

client = MongoClient('localhost', 27017)
db = client['news_db']

try:
    collection = db.create_collection('news')
except BaseException:
    collection = db.news

headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.93'}
URLS = ['https://lenta.ru', 'https://news.mail.ru', 'https://yandex.ru/news/']


def news_mail(url, headers, collection):
    response = requests.get(url, headers=headers)
    page = html.fromstring(response.text)
    news_div = page.xpath('//table[@class="daynews__inner"]//a/@href')
    for i in news_div:
        response_data = requests.get(i, headers=headers)
        date_time = html.fromstring(response_data.text)
        news = {
            'title': date_time.xpath('//h1/text()')[0],
            'url_news': i,
            'date': date_time.xpath('//span[@datetime]/@datetime')[0],
            'source': date_time.xpath(
                '//span[contains(text(), "источник")]/following-sibling::node()/@href')[0]
        }
        try:
            if validate(collection, news['url_news']):
                collection.insert_one(news)
        except BaseException:
            continue


def news_yandex(url, headers, collection):
    response = requests.get(url, headers=headers)
    page = html.fromstring(response.text)
    news_div = page.xpath('//article')[:5]
    for i in news_div:
        news = {
            'title': i.xpath('..//h2/text()')[0].replace(
                '\xa0',
                ' '),
            'url_news': i.xpath('..//a/@href')[0],
            'date': i.xpath('..//span[@class="mg-card-source__time"]/text()')[0],
            'source': i.xpath('..//a/text()')[0]
        }
        try:
            if validate(collection, news['url_news']):
                collection.insert_one(news)
        except BaseException:
            continue


def news_lenta(url, collection):
    free = FreeProxy()
    proxies = free.get_proxy_list()
    response = requests.get(url, headers={'User-Agent': UserAgent().chrome})
    page = html.fromstring(response.text)
    news_div = page.xpath(
        '//section/div[contains(@class, "b-yellow-box__wrap")]/div[contains(@class, "item")]/a')
    for i in news_div:
        k = len(proxies) - 1
        n = randint(0, k)
        news = {'title': i.xpath('..//text()')[0].replace('\xa0', ' '), 'source': url}
        url_news = url + i.xpath('..//@href')[0]
        news['url_news'] = url_news
        response_data = requests.get(url_news, headers={'User-Agent': UserAgent().chrome}, proxies={'http': proxies[n]})
        date_time = html.fromstring(response_data.text)
        date = date_time.xpath('//div[contains(@class, "topic__info")]/time/@datetime')[0]
        news['date'] = date
        time.sleep(1)
        try:
            if validate(collection, news['url_news']):
                collection.insert_one(news)
        except BaseException:
            continue


def validate(collection, url):
    return db.collection.find({'url': url}) is None


news_mail(URLS[1], headers, collection)
news_yandex(URLS[2], headers, collection)
news_lenta(URLS[0], collection)
