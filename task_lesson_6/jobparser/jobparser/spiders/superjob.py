import scrapy
from urllib.parse import urlencode
from bs4 import BeautifulSoup as bs
import re


from jobparser.items import JobparserItem


class SuperjobSpider(scrapy.Spider):
    name = 'https://www.superjob.ru'
    allowed_domains = ['superjob.ru']

    params = {'clusters': 'true',
              'keywords': 'java developer',
              'page': 0
              }
    url = 'https://www.superjob.ru/vacancy/search/?' + urlencode(params)
    start_urls = [url]

    def parse(self, responce):
        dom = bs(responce.text, 'html.parser')
        vacancy_link = dom.find_all('a', {'class': re.compile('icMQ_ _6AfZ9')})
        vacancy_link = list(map(lambda item: 'https://www.superjob.ru' + item['href'], vacancy_link))

        for item in vacancy_link:
            yield responce.follow(item, callback=self.get_resume)

        domain = 'https://www.superjob.ru/'
        next_link = dom.find('a', text='Дальше')['href']

        if next_link != None:
            next_page = domain + next_link
            yield responce.follow(next_page, callback=self.parse)

    def get_resume(self, responce):
        dom = bs(responce.text, 'html.parser')
        domain = self.name
        link = responce.url
        name = dom.find('h1').text
        salary_string = dom.find('span', {'class': '_1h3Zg _2Wp8I _2rfUm _2hCDz'}).text

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
                                  link=link,
                                  name=name,
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