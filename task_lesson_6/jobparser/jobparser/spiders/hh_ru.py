import scrapy
from scrapy.http import HtmlResponse
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs
import re
from jobparser.items import JobparserItem


class HhRuSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    params = {'clusters': 'true',
              'area': 1,
              'enable_snippets': 'true',
              'st': 'searchVacancy',
              'text': 'java developer',
              'page': 0
              }

    url = 'http://hh.ru/search/vacancy/?' + urlencode(params)
    start_urls = [url]

    def parse(self, response: HtmlResponse):

        vacancies_links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").extract()
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").extract_first()
        for link in vacancies_links:
            yield response.follow(link, callback=self.vacansy_parse)

        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def vacansy_parse(self, response: HtmlResponse):
        domain = 'http://hh.ru'
        vacancy_name = response.xpath("//h1/text()").extract_first()
        link = response.url
        vacancy_salary = response.xpath("//p[@class='vacancy-salary']/span/text()").extract()
        salary_string = " ".join(vacancy_salary)


        min_salary = None
        max_salary = None
        currency = None

        # Заполнение зарплатных данных (может быть Null)
        if salary_string is None or len(self.salary_split(salary_string)) == 0:
            return [min_salary, max_salary, currency]
        elif len(self.salary_split(salary_string)) == 2:
            min_salary = int(self.salary_split(salary_string)[0])
            max_salary = int(self.salary_split(salary_string)[1])
        elif salary_string.find("от") != -1 and len(self.salary_split(salary_string)) == 1:
            min_salary = int(self.salary_split(salary_string)[0])
            max_salary = None
        else:
            min_salary = None
            max_salary = int(self.salary_split(salary_string)[0])

        # В какой валюте зарплата (может быть Null)
        if salary_string.find("руб") != -1:
            currency = "руб"
        elif salary_string.find("USD") != -1:
            currency = "USD"
        else:
            currency = None
        yield JobparserItem(domain=domain,
                            name=vacancy_name,
                            link=link,
                            min_salary=min_salary,
                            max_salary=max_salary,
                            currency=currency)

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
