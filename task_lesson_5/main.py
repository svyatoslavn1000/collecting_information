# Написать программу, которая собирает входящие письма из своего или тестового почтового ящика
# и сложить данные о письмах в базу данных (от кого, дата отправки, тема письма, текст письма полный)

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import user


client = MongoClient('localhost', 27017)
db = client['letters']
db.letters_m.drop()
collection = db.create_collection('letters_m')

user = user.User()
user_name = user.login
user_pass = user.password
url = 'https://light.mail.ru/'

chrome_options = Options()
chrome_options.add_argument('start-maximized')
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)

driver.get(url)

def log_in(login, password):
    elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username")))
    elem.send_keys(login)
    elem.send_keys(Keys.ENTER)

    elem = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password")))
    elem.send_keys(password)
    elem.send_keys(Keys.ENTER)


def parcing_letters_list():
    all_links = []
    while True:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//tr[@class='messageline' or contains(@class,'_unread')]")))
        letters = driver.find_elements_by_xpath("//tr[@class='messageline' or contains(@class,'_unread')]")
        for letter in letters:
            link = letter.find_element_by_xpath(
                "td[@class='messageline__subject messageline__item']/a[@class='messageline__link']")\
                .get_attribute('href')
            all_links.append(link)
        try:
            next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//a[@title='Далее']")))
            next_button.click()
        except TimeoutException:
            break
    for link in all_links:
        insert_to_db(parce_letter(link))

def insert_to_db(letter):
    try:
        collection.insert_one(letter)
    except Exception:
        print('письмо не добавлено в БД')

def parce_letter(link):

    driver.get(link)
    letter = {}

    letter['_id'] = link.split('/')[-2]
    letter['url'] = link
    # Это велосипед, но по другому не получается :(
    try:
        letter['from'] = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='mr_read__fromf']"))).text
    except TimeoutException:
        letter['from'] = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.XPATH, "//span[@class='val']"))).text
    letter['sender_email'] = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.XPATH, "//a[@class='mr_ico mr_read__findall']"))).get_attribute(
        'href').split('=')[-1]
    letter['text'] = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'cl_')]"))).text
    letter['datetime'] = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.XPATH, "//span[@id='msgFieldDate']/span"))).text

    return letter


log_in(user_name, user_pass)

parcing_letters_list()