# должность) с сайтов Superjob(по желанию) и HH(обязательно). Приложение должно анализировать несколько страниц сайта
# (также вводим через input или аргументы). Получившийся список должен содержать в себе минимум:
#
# Наименование вакансии. Предлагаемую зарплату (отдельно минимальную и максимальную). Ссылку на саму вакансию. Сайт,
# откуда собрана вакансия. По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
# Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame
# через pandas. Сохраните в json либо csv.

import requests
import bs4
from urllib.parse import urljoin
from urllib.parse import urlencode
import time
import typing
import csv
from pathlib import Path
import lxml.html as html
import pandas as pd


class HHParse:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
    }
    __parse_time = 0

    def __init__(self, delay=1.0):
        initial_conditions = self.get_url()
        self.start_url = initial_conditions[1]
        self.name = initial_conditions[0]
        self.delay = delay
        self.done_urls = set()
        self.tasks = []
        self.headlines = ['Name', 'Url', 'Min_salary', 'Max_salary', 'Currency' 'Sourse']
        self.data = []
        self.save_path = self.get_save_path()
        self.file_path = self.save_path.joinpath(f"{self.name}.csv")

    def _get_response(self, url):
        while True:
            next_time = self.__parse_time + self.delay
            if next_time > time.time():
                time.sleep(next_time - time.time())
            response = requests.get(url, headers=self.headers)
            print(f"RESPONSE: {response.url}")
            self.__parse_time = time.time()
            if response.status_code == 200:
                return response

    def run_parsing(self):
        # self.create_csv(self.headlines, self.file_path)
        page_urls = self.parse_pagination(self._get_response(self.start_url))
        for item in page_urls:
            for link in self.search_vacancy_links(self._get_response(item)):
                response = self._get_response(link)
                self.parse_vacancy(response)

    def parse_pagination(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')

        pagination = soup.find_all('a', attrs={"data-qa": "pager-page"})
        pagination_links = set(
            urljoin(response.url, itm.attrs.get('href'))
            for itm in pagination if
            itm.attrs.get("href")
        )
        return pagination_links


    def search_vacancy_links(self, response: requests.Response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        vacancies = soup.find_all('a', attrs={"data-qa": "vacancy-serp__vacancy-title"})
        vacancy_links = set(
            itm.attrs.get('href')
            for itm in vacancies)
        return vacancy_links


    def parse_vacancy(self, response):
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        url = response.url
        # Id вакансии на сайте hh
        if len(url) == 0:
            vacancy_hh_id = None
        else:
            try:
                vacancy_hh_id = url.split('/')[4].split("?")[0]
            except IndexError:
                vacancy_hh_id = None
        vacancy_name = soup.find('h1', attrs={"data-qa": "vacancy-title"}).text
        salary = self.parse_salary(soup.find('span', attrs={"data-qa": "bloko-header-2"}).text)
        vacancy = [vacancy_hh_id, vacancy_name, url, salary[0], salary[1], salary[2], 'hh.ru']
        self._save(vacancy)

    def parse_salary(self, vacancy_salary: str):

        vacancy_salary_min = None
        vacancy_salary_max = None
        vacancy_salary_in = None

        # Заполнение зарплатных данных (может быть Null)
        if vacancy_salary is None or len(vacancy_salary) == 0:
            [vacancy_salary_min, vacancy_salary_max, vacancy_salary_in]
        elif vacancy_salary.find("-") != -1:
            vacancy_salary_min = vacancy_salary.split('-')[0].replace(u'\xa0', u'')
            vacancy_salary_max = vacancy_salary.split('-')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u'')
        elif vacancy_salary.find("от") != -1:
            vacancy_salary_min = vacancy_salary.split('от')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u'')
            vacancy_salary_max = None
        elif vacancy_salary.find("до") != -1:
            vacancy_salary_min = None
            vacancy_salary_max = vacancy_salary.split('до')[1].split("руб")[0].split("USD")[0].replace(u'\xa0', u'')

        # В какой валюте зарплата (может быть Null)
        if vacancy_salary.find("руб") != -1:
            vacancy_salary_in = "руб"
        elif vacancy_salary.find("USD") != -1:
            vacancy_salary_in = "USD"
        else:
            vacancy_salary_in = None
        return [vacancy_salary_min, vacancy_salary_max, vacancy_salary_in]


    def _save(self, vacancy: list):
        self.write_row_to_csv(vacancy, self.file_path)

    def create_csv(self, headlines, path):
        with open(path, "w", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(headlines)

    def write_row_to_csv(self, vacancy, path):
        with open(path, "a", newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow(vacancy)

    def get_save_path(self) -> Path:
        dir_name = input('Введите название директории: ')
        save_path = Path(__file__).parent.joinpath(dir_name)
        if not save_path.exists():
            save_path.mkdir()
        return save_path

    def get_url(self):
        hh_url = 'https://hh.ru/search/vacancy?'
        name = str(input('Введите название искомой вакансии: '))
        vacancy_request = {'text': name}
        vacancy_request = urlencode(vacancy_request)
        url = str(hh_url + vacancy_request)
        init = [name, str(url)]
        return init



if __name__ == '__main__':
    parser = HHParse()
    parser.run_parsing()



