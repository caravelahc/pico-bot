import os
import pickle
import time

from .user_entity import UserEntity


def repository(database_path: str = None):
    if Repo.instance is None:
        Repo.instance = Repo(database_path)
    return Repo.instance


class Repo(object):
    instance = None

    def __init__(self, database_path: str = None):
        self._db = ''
        self._users = {}
        self._public_packs = set()

        if database_path is not None:
            self._load_db(database_path)

    def users(self):
        return self._users

    def packs(self):
        return self._public_packs

    def add_pack_to_user(self, user, pack_name: str):
        if user.id not in self._users:
            self._users[user.id] = UserEntity(user)

        self._users[user.id].packs.add(pack_name)
        self._update_db()

    def check_permission(self, user_id: int, pack_name: str):
        if pack_name in self._public_packs:
            return True
        return user_id in self._users and \
            pack_name in self._users[user_id].packs

    def set_pack_public(self, pack_name: str, is_public: bool):
        if is_public:
            self._public_packs.add(pack_name)
        elif pack_name in self._public_packs:
            self._public_packs.remove(pack_name)
        self._update_db()

    def _load_db(self, db_path: str):
        self._db = db_path
        if os.path.exists(db_path):
            fp = open(db_path, 'rb')
            data = pickle.load(fp)
            self._users = data['users']
            self._public_packs = data['packs']
            fp.close()

    def _update_db(self):
        data = {
            'users': self._users,
            'packs': self._public_packs
        }
        fp = open(self._db, 'wb')
        pickle.dump(data, fp)
        fp.close()
