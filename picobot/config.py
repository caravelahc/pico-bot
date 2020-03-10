import json
from os import environ, path
from pathlib import Path

ROOT_DIR = path.dirname(path.abspath(__file__))

try:
    CONFIG_DIR = Path(environ['XDG_CONFIG_HOME'], 'picobot')
except KeyError:
    CONFIG_DIR = Path.home() / '.config' / 'picobot'

try:
    with open(CONFIG_DIR / 'config.json') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {}

TOKEN = config['token']
DB_PATH = config.get('db_path', CONFIG_DIR / 'bot.db')
CREATOR_ID = config.get('creator_id', 206454394)
