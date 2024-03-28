import json
from functools import lru_cache
from os import environ
from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parent

@lru_cache(1)
def get_config_dir() -> Path:
    if 'PICOBOT_CONFIG_DIR' in environ:
        return Path(environ['PICOBOT_CONFIG_DIR'])

    if 'XDG_CONFIG_HOME' in environ:
        return Path(environ['XDG_CONFIG_HOME']) / 'picobot'

    return Path.home() / '.config' / 'picobot'

CONFIG_DIR = get_config_dir()

with open(CONFIG_DIR / 'config.json') as f:
    config = json.load(f)

TOKEN = config['token']
DB_PATH = config.get('db_path', CONFIG_DIR / 'bot.db')
CREATOR_ID = config['creator_id']
