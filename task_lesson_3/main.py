# 1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать
# функцию, записывающую собранные вакансии в созданную БД. Решение --- строка 60
# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой
# больше введённой суммы. --- Функция реализована в класс VacaniesRepository
# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.
# --- Реализовано по полю 'url' в методе create в классе VacaniesRepository

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
from vacancy import Vacancy
from vacanciesRepository import VacanciesRepository
from pymongo import MongoClient


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
        repository = VacanciesRepository()
        page_urls = self.parse_pagination(self._get_response(self.start_url))
        for item in page_urls:
            for link in self.search_vacancy_links(self._get_response(item)):
                response = self._get_response(link)

                # Решение задания 1.

                vacancy = self.parse_vacancy(response)
                repository.create(vacancy)


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
            vacancy_id = None
        else:
            try:
                vacancy_id = url.split('/')[4].split("?")[0]
            except IndexError:
                vacancy_id = None
        vacancy_name = soup.find('h1', attrs={"data-qa": "vacancy-title"}).text
        salary = self.parse_salary(soup.find('span', attrs={"data-qa": "bloko-header-2"}).text)
        vacancy = Vacancy(vacancy_id, vacancy_name, url, salary[0],  salary[1], salary[2])
        # self._save(vacancy)
        return vacancy

    def parse_salary(self, vacancy_salary: str):

        vacancy_salary_min = None
        vacancy_salary_max = None
        vacancy_salary_in = None

        # Заполнение зарплатных данных (может быть Null)
        if vacancy_salary is None or len(self.salary_split(vacancy_salary)) == 0:
            return [vacancy_salary_min, vacancy_salary_max, vacancy_salary_in]
        elif len(self.salary_split(vacancy_salary)) == 2:
            print(vacancy_salary)
            print(self.salary_split(vacancy_salary))
            vacancy_salary_min = int(self.salary_split(vacancy_salary)[0])
            vacancy_salary_max = int(self.salary_split(vacancy_salary)[1])
        elif vacancy_salary.find("от") != -1 and len(self.salary_split(vacancy_salary)) == 1:
            vacancy_salary_min = int(self.salary_split(vacancy_salary)[0])
            vacancy_salary_max = None
        else:
            vacancy_salary_min = None
            vacancy_salary_max = int(self.salary_split(vacancy_salary)[0])

        # В какой валюте зарплата (может быть Null)
        if vacancy_salary.find("руб") != -1:
            vacancy_salary_in = "руб"
        elif vacancy_salary.find("USD") != -1:
            vacancy_salary_in = "USD"
        else:
            vacancy_salary_in = None
        return [vacancy_salary_min, vacancy_salary_max, vacancy_salary_in]

    def salary_split(self, s):
        l = len(s)
        integ = []
        i = 0
        while i < l:
            s_int = ''
            a = s[i]
            while '0' <= a <= '9':
                s_int += a
                i += 1
                if i < l:
                    a = s[i]
                else:
                    break
            i += 1

            if s_int != '':
                integ.append(s_int)

            for j in range(len(integ)):
                if integ[j][0] == '0':
                    a = integ.pop(j)
                    integ[j - 1] = f'{integ[j - 1]}{a}'

        return integ


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
    repository = VacanciesRepository()
    repository.find_salary_by_limit(100000)

    # repository = VacanciesRepository()
    # print(repository.find_salary_by_limit(100000))
    parser = HHParse()
    parser.run_parsing()



