import dataset
from telegram import User

from .user_entity import UserEntity


def repository(database_path: str = None):
    if Repo.instance is None:
        Repo.instance = Repo(database_path)
    return Repo.instance


def fake_startup():
    r = repository()
    tarcisio = UserEntity(User(18471616, 'Tarcisio', False, 'Crocomo', 'tarcisioe'))
    tarcisio.packs = set(['meupackzera_by_HitchhikersBot', 'guaxinim_by_HitchhikersBot', 'llamas_by_HitchhikersBot', 'bonde_by_HitchhikersBot'])
    tarcisio.def_pack = 'guaxinim_by_HitchhikersBot'
    diogo = UserEntity(User(206454394, 'Diogo', False, 'Junoir', 'diogojs'))
    diogo.packs.add('FavoriteBarnei_by_HitchhikersBot')
    r._users = {
        18471616: tarcisio,
        206454394: diogo
    }
    r._packs = {'PicoTestPk_by_HitchhikersBot': True, 'zipzap_by_HitchhikersBot': False}


class Repo(object):
    instance = None

    def __init__(self, database_path: str = None):
        self._db = None
        self._users = {}
        self._packs = {}

        if database_path is not None:
            self._create_or_connect_to_db(database_path)

    def users(self):
        return self._users

    def packs(self):
        return self._packs

    def add_pack_to_user(self, user_id: int, pack_name: str):
        self._users[user_id].packs.add(pack_name)

    def check_permission(self, user_id: int, pack_name: str):
        if self._packs.get(pack_name):
            return True
        return user_id in self._users and \
            pack_name in self._users[user_id].packs

    def _create_or_connect_to_db(self, db_path: str):
        self._db = dataset.connect(f'sqlite:///{db_path}')

    def _db_add_user(self, user: UserEntity):
        if self._db is None:
            return

        table = self._db.get_table('users', primary_id='id')
        existent = table.find_one(id=user.t_user.id)
        if not existent:
            table.insert(id=user.t_user.id)
