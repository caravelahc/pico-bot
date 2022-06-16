import json
from os import environ
from pathlib import Path

ROOT_DIR = Path(__file__).absolute().parent

try:
    CONFIG_DIR = Path(environ['XDG_CONFIG_HOME'], 'picobot')
except KeyError:
    CONFIG_DIR = Path.home() / '.config' / 'picobot'

with open(CONFIG_DIR / 'config.json', encoding='utf8') as f:
    config = json.load(f)

TOKEN = config['token']
DB_PATH = config.get('db_path', CONFIG_DIR / 'bot.db')
CREATOR_ID = config.get('creator_id', 206454394)
