from instabot import Bot
from instaparser.user_config import INSTA_LOGIN, PASS

class BotInstagram:
    bot = Bot()
    bot.login(username=INSTA_LOGIN, password=PASS)

    def __init__(self, username):
        self.username = username

    # Список подписчиков
    def get_followers(self):
        user_followers = self.bot.get_user_followers(self.username)
        dict = {}
        for uf in user_followers:
            dict[uf] = self.bot.get_username_from_user_id(uf)
        return dict

    # Список подписок
    def get_following(self, ):
        user_following = self.bot.get_user_following(self.username)
        dict = {}
        for uf in user_following:
            dict[uf] = self.bot.get_username_from_user_id(uf)
        return dict