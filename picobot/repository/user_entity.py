from telegram import User


class UserEntity():

    def __init__(self, t_user: User):
        self.t_user = t_user
        self.state = ''
        self.packs = set()
        self.def_pack = None
