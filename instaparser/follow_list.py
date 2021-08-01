from instaparser.user_config import TARGETS
from instaparser.bot import BotInstagram

class UserList:
    users = TARGETS
    list = []
    def followings_list(self):
        for t in self.users:
            followings = BotInstagram(t).get_following()
            for i in followings:
                list.append({'gen_user': t, 'user': i})
        return list

    def followers_list(self):
        for t in self.users:
            followers = BotInstagram(t).get_followers()
            for i in followers:
                list.append({'gen_user': t, 'user': i})
        return list