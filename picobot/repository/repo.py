import os
import time
import pickle

from .user_entity import UserEntity


BACKUP_TIME = 3600  # seconds


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
        """ Save data to disk if passed BACKUP_TIME from last update
            @Returns:
                True if data saved
                False otherwise
        """
        last_update = 0
        if os.path.exists(self._db):
            last_update = os.path.getmtime(self._db)

        if time.time() > (last_update + BACKUP_TIME):
            self._force_update_db(self._db)
            return True
        return False

    def _force_update_db(self, db_path: str):
        data = {
            'users': self._users,
            'packs': self._public_packs
        }
        fp = open(db_path, 'wb')
        pickle.dump(data, fp)
        fp.close()
