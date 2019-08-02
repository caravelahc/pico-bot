import logging
import dataset
from telegram import Bot, Update

from functools import wraps

from .config import CREATOR_ID, DB_PATH
from picobot import responses
from .painter import sticker_from_text

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

EMOJI = '😁'


def creator_only(func):
    @wraps(func)
    def new_func(bot, update, *args, **kwargs):
        if update.message.from_user.id == CREATOR_ID:
            return func(bot, update, *args, **kwargs)
        else:
            update.message.reply_text(responses.ACCESS_DENIED)

    return new_func


def text_handler(bot, update):
    pass


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text(responses.GREETING)


def new_pack(bot, update):
    db = dataset.connect(f'sqlite:///{DB_PATH}')
    table = db.get_table('users', primary_id='id')
    user_id = update.message.from_user.id
    user = table.find_one(id=user_id)
    if not user:
        table.insert(id=user_id)

    pack_number = create_pack()
    if pack_number == 0:
        update.message.reply_text(responses.ERROR_MSG)
    else:
        update.message.reply_text(f'{responses.PACK_CREATED}: {pack_number}')


def create_pack(bot: Bot, update: Update):
    user_id = update.message.from_user.id
    title = update.message.text.split(' ')[1]
    name = title + '_by_HitchhikersBot'
    png_sticker = open('images/caravela.png', 'rb')
    emojis = update.message.text.split(' ')[2]

    # Create Pack
    if bot.create_new_sticker_set(user_id=user_id, name=name, title=title, png_sticker=png_sticker, emojis=EMOJI):
        sticker = bot.get_sticker_set(name).stickers[0]
        update.message.reply_sticker(sticker)
    png_sticker.close()


def add_sticker(bot: Bot, update: Update):
    msg_type = 'MSG_TYPE.TEXT'
    response = 'oopsie'
    # check if it's image, file, text, or sticker
    if msg_type == 'MSG_TYPE.IMAGE':
        # check if format of msg is right
        # save as png
        # send to @Stickers
        response = 'NOT IMPLEMENTED'
    elif msg_type == 'MSG_TYPE.FILE':
        # check if format of msg is right
        # send to @Stickers
        response = 'NOT IMPLEMENTED'
    elif msg_type == 'MSG_TYPE.TEXT':
        # check if format of msg is right
        user_id = update.message.from_user.id
        pack_name = update.message.text.split(' ')[1]
        emojis = update.message.text.split(' ')[2]
        username = update.message.reply_to_message.forward_from.full_name
        text = update.message.reply_to_message.text
        # save as png
        img_path = sticker_from_text(user_id, username, text)
        png_sticker = open(img_path, 'rb')
        if bot.add_sticker_to_set(user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emojis):
            sticker = bot.get_sticker_set(pack_name).stickers[-1]
            update.message.reply_sticker(sticker)
            response = 'Sticker adicionado!'
        png_sticker.close()
    elif msg_type == 'MSG_TYPE.STICKER':
        # check if format of msg is right
        # save as png
        # send to @Stickers
        response = 'NOT IMPLEMENTED'

    # check if there is any error

    update.message.reply_text(response)


def del_sticker(bot, update):
    # check format of msg
    # send to @Stickers
    update.message.reply_text('NOT IMPLEMENTED')


def handler_help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(responses.HELP_MSG)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)