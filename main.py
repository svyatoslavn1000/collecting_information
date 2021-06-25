from github import Github
import requests

# 1. Выводит все мои публичные репозитории
username = "svyatoslavn1000"
g = Github()
user = g.get_user(username)
for repo in user.get_repos():
    print(repo)

# Другой вариант

req = requests.get("https://api.github.com/users/svyatoslavn1000/repos")

with open('data.txt', 'w') as f:
    f.write(req.text)

# 2.
def weather(api_key):
    print("Введите название города")
    city = input()
    x = f"api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    print(x)
    req = requests.get(f" http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}")

    return req.text


print(weather('106b6f58c1bd0cfd53e4504c80ff9c05'))