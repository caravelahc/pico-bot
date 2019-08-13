import logging
import dataset
from telegram import Bot, Update, Message

from functools import wraps

from .config import CREATOR_ID, DB_PATH, ROOT_DIR
from picobot import responses
from .msg_type import MsgType
from .painter import sticker_from_text, sticker_from_image

IMG_DIR = ROOT_DIR + '/images/'
IMG_NAME = 'img'
AVATAR_NAME = 'avatar'

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DEFAULT_EMOJI = '😁'


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
    if not check_msg_format(update.message.text):
        update.message.reply_text(responses.INVALID_MSG)
    splittext = update.message.text.split()
    title = splittext[1]
    name = title + '_by_' + bot.username
    png_sticker = open('images/caravela.png', 'rb')
    if len(splittext) > 2:
        emoji = update.message.text.split()[2]
    else:
        emoji = DEFAULT_EMOJI

    # Create Pack
    if bot.create_new_sticker_set(user_id=user_id, name=name, title=title, png_sticker=png_sticker, emojis=emoji):
        sticker = bot.get_sticker_set(name).stickers[0]
        update.message.reply_sticker(sticker)
    png_sticker.close()


def add_sticker(bot: Bot, update: Update):
    msg: Message = update.message
    msg_type = get_msg_type(msg)
    response = responses.ERROR_MSG

    # check if it's image, file, text, or sticker
    if msg_type == MsgType.TEXT:
        if add_text(bot, msg):
            response = responses.ADDED_STICKER
    elif msg_type == MsgType.PHOTO:
        if add_photo(bot, msg, False):
            response = responses.ADDED_STICKER
    elif msg_type == MsgType.REP_PHOTO:
        if add_photo(bot, msg, True):
            response = responses.ADDED_STICKER
    elif msg_type == MsgType.DOCUMENT:
        if add_document(bot, msg, False):
            response = responses.ADDED_STICKER
    elif msg_type == MsgType.REP_DOCUMENT:
        if add_document(bot, msg, True):
            response = responses.ADDED_STICKER

    elif msg_type in [MsgType.STICKER, MsgType.REP_STICKER]:
        if insert_sticker_in_pack(bot, msg):
            response = responses.ADDED_STICKER

    # check for errors

    update.message.reply_text(response)


def add_text(bot: Bot, msg: Message):
    if not check_msg_format(msg.text):
        # TODO: if user has only one pack, use that as default
        msg.reply_text(responses.INVALID_MSG)
        return

    user_id = msg.from_user.id
    splittext = msg.text.split()
    pack_name = splittext[1] + '_by_' + bot.username
    if len(splittext) > 2:
        emoji = msg.text.split()[2]
    else:
        emoji = DEFAULT_EMOJI

    forward = msg.reply_to_message.forward_from
    if forward is not None:
        username = forward.first_name
        other_user_id = forward.id
    else:
        username = msg.reply_to_message.from_user.first_name
        other_user_id = msg.reply_to_message.from_user.id
    photos = bot.get_user_profile_photos(other_user_id, limit=1).photos
    avatar_path = ''
    try:
        photo = photos[0][0]
        avatar_path = IMG_DIR + AVATAR_NAME + str(other_user_id) + '.jpg'
        bot.get_file(photo.file_id).download(custom_path=avatar_path)
    except Exception:
        msg.reply_text(responses.ERROR_DOWNLOAD_PHOTO)

    text = msg.reply_to_message.text
    # save as png
    img_path = sticker_from_text(user_id, username, text, avatar_path)
    png_sticker = open(img_path, 'rb')
    try:
        bot.add_sticker_to_set(user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji)
        sticker = bot.get_sticker_set(pack_name).stickers[-1]
        msg.reply_sticker(sticker)
    except Exception:
        return False
    finally:
        png_sticker.close()
    return True


def caption_handler(bot: Bot, update: Update):
    text = update.message.caption
    if text is None or text == '':
        return
    if not check_msg_format(text):
        # TODO: if user has only one pack, use that as default
        update.message.reply_text(responses.INVALID_MSG)
        return
    if text.split()[0] == '/addsticker':
        update.message.text = text
        add_sticker(bot, update)


def check_msg_format(text: str):
    return text is not None and len(text.split()) > 1


@creator_only
def check_msg_type(bot: Bot, update: Update):
    msg_type = get_msg_type(update.message)
    if msg_type is None:
        update.message.reply_text(responses.INVALID_MSG)
        handler_help(bot, update)
    else:
        update.message.reply_text(msg_type.name)


def get_msg_type(message: Message):
    replied = False
    if message.reply_to_message is not None:
        replied = True
        message = message.reply_to_message

    if message.photo is not None and len(message.photo) > 0:
        msg_type = MsgType.PHOTO
    elif message.sticker is not None:
        msg_type = MsgType.STICKER
    elif message.document is not None:
        msg_type = MsgType.DOCUMENT
    elif message.text is not None:
        return MsgType.TEXT if replied else None

    if replied:
        return MsgType(msg_type * 10)
    else:
        return msg_type


def add_photo(bot: Bot, msg: Message, replied: bool):
    user_id = msg.from_user.id
    splittext = msg.text.split()
    pack_name = splittext[1] + '_by_' + bot.username
    if len(splittext) > 2:
        emoji = msg.text.split()[2]
    else:
        emoji = DEFAULT_EMOJI
    if replied:
        photo = msg.reply_to_message.photo[-1]
    else:
        photo = msg.photo[-1]
    img_path = IMG_DIR + IMG_NAME + str(user_id) + '.jpg'
    try:
        bot.get_file(photo.file_id).download(custom_path=img_path)
        # resize and save as png
        img_path = sticker_from_image(img_path)
        png_sticker = open(img_path, 'rb')
        bot.add_sticker_to_set(user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji)
        sticker = bot.get_sticker_set(pack_name).stickers[-1]
        msg.reply_sticker(sticker)
    except Exception:
        return False
    return True


def add_document(bot: Bot, msg: Message, replied: bool):
    user_id = msg.from_user.id
    splittext = msg.text.split()
    pack_name = splittext[1] + '_by_' + bot.username
    if len(splittext) > 2:
        emoji = msg.text.split()[2]
    else:
        emoji = DEFAULT_EMOJI
    if replied:
        doc = msg.reply_to_message.document
    else:
        doc = msg.document

    try:
        bot.add_sticker_to_set(user_id=user_id, name=pack_name, png_sticker=doc.file_id, emojis=emoji)
        sticker = bot.get_sticker_set(pack_name).stickers[-1]
        msg.reply_sticker(sticker)
    except Exception:
        msg.reply_text(responses.INVALID_DOC)
        return False
    return True


def insert_sticker_in_pack(bot: Bot, msg: Message):
    user_id = msg.from_user.id
    splittext = msg.text.split()
    pack_name = splittext[1] + '_by_' + bot.username
    if len(splittext) > 2:
        emoji = msg.text.split()[2]
    else:
        emoji = DEFAULT_EMOJI
    sticker_id = msg.reply_to_message.sticker.file_id

    img_path = IMG_DIR + IMG_NAME + str(user_id) + '.jpg'
    try:
        bot.get_file(sticker_id).download(custom_path=img_path)
        # resize and save as png
        img_path = sticker_from_image(img_path)
        png_sticker = open(img_path, 'rb')
        bot.add_sticker_to_set(user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji)
        sticker = bot.get_sticker_set(pack_name).stickers[-1]
        msg.reply_sticker(sticker)
    except Exception:
        return False
    return True


def del_sticker(bot, update):
    # check format of msg
    update.message.reply_text('NOT IMPLEMENTED')


def handler_help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text(responses.HELP_MSG)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
