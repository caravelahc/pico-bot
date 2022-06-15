import logging
import os
import shlex
from functools import wraps

import telegram
from slugify import slugify
from telegram import Bot, Message, Update
from telegram.ext import CallbackContext

from picobot import responses

from .config import CREATOR_ID, ROOT_DIR
from .msg_type import MsgType
from .painter import sticker_from_image, sticker_from_text
from .repository.repo import repository

IMG_DIR = ROOT_DIR / 'images'
IMG_PREFIX = 'img'
AVATAR_PREFIX = 'avatar'

logging.basicConfig(
    filename='log_picobot.log',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

DEFAULT_EMOJI = '😁'


def creator_only(func):
    @wraps(func)
    def new_func(bot, update, *args, **kwargs):
        if update.message.from_user.id == CREATOR_ID:
            return func(bot, update, *args, **kwargs)
        else:
            update.message.reply_text(responses.CREATOR_ACCESS_DENIED)

    return new_func


def build_pack_name(title: str, bot: Bot) -> str:
    slug = slugify(title, separator="_", lowercase=False)
    return f'{slug}_by_{bot.username}'


def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(responses.GREETING)


def create_pack(update: Update, context: CallbackContext):
    bot = context.bot
    user = update.message.from_user

    if not check_msg_format(update.message.text):
        update.message.reply_text(responses.INVALID_MSG)
        return

    splittext = shlex.split(update.message.text)

    title = splittext[1]
    name = build_pack_name(title, bot)
    png_sticker = open(IMG_DIR / 'caravela.png', 'rb')
    emoji = splittext[2] if len(splittext) > 2 else DEFAULT_EMOJI

    # Create Pack
    try:
        bot.create_new_sticker_set(
            user_id=user.id,
            name=name,
            title=title,
            png_sticker=png_sticker,
            emojis=emoji,
        )
        sticker = bot.get_sticker_set(name).stickers[0]
        update.message.reply_sticker(sticker)
        repository().add_pack_to_user(user, name)
    except Exception as exc:
        logger.error(
            "Exception on Create Pack. User %s (id %d) Pack %s",
            user.first_name,
            user.id,
            name,
        )

        logger.error(exc)
        update.message.reply_text(responses.ERROR_MSG)
    png_sticker.close()


def add_sticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg = update.message

    msg_type = get_msg_type(msg)
    response = responses.ERROR_MSG
    user_id = msg.from_user.id
    splittext = shlex.split(msg.text)

    if check_msg_format(msg.text):
        title = splittext[1]
        pack_name = build_pack_name(title, bot)

        # check if user is pack's owner
        if not repository().check_permission(user_id, pack_name):
            msg.reply_text(responses.NO_PERMISSION)
            return

    else:  # if pack name not informed check if user has default pack
        user = repository().users().get(user_id)

        if user is not None and user.def_pack is not None:
            pack_name = user.def_pack
        else:
            msg.reply_text(responses.INVALID_MSG)
            return

    if len(splittext) > 2:
        emoji = splittext[2]
    else:
        emoji = DEFAULT_EMOJI

    # check if it's image, file, text, or sticker
    if msg_type == MsgType.REP_TEXT:
        if add_text(bot, msg, user_id, pack_name, emoji):
            return
    elif msg_type == MsgType.PHOTO:
        if add_photo(bot, msg, user_id, pack_name, emoji, False):
            return
    elif msg_type == MsgType.REP_PHOTO:
        if add_photo(bot, msg, user_id, pack_name, emoji, True):
            return
    elif msg_type == MsgType.DOCUMENT:
        if add_document(bot, msg, user_id, pack_name, emoji, False):
            return
    elif msg_type == MsgType.REP_DOCUMENT:
        if add_document(bot, msg, user_id, pack_name, emoji, True):
            return
    elif msg_type in [MsgType.STICKER, MsgType.REP_STICKER]:
        if insert_sticker_in_pack(bot, msg, user_id, pack_name, emoji):
            return

    # check for errors

    update.message.reply_text(response)


def add_text(bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str):
    forward = msg.reply_to_message.forward_from
    if forward is not None:
        username = forward.first_name
        other_user_id = forward.id
        msg_time = msg.reply_to_message.forward_date.strftime('%H:%M')
    else:
        username = msg.reply_to_message.from_user.first_name
        other_user_id = msg.reply_to_message.from_user.id
        msg_time = msg.reply_to_message.date.strftime('%H:%M')
    photos = bot.get_user_profile_photos(other_user_id, limit=1).photos
    avatar_path = ''
    try:
        photo = photos[0][0]
        avatar_path = IMG_DIR / f'{AVATAR_PREFIX}{other_user_id}.jpg'
        bot.get_file(photo.file_id).download(custom_path=avatar_path)
    except Exception:
        msg.reply_text(responses.ERROR_DOWNLOAD_PHOTO)
        avatar_path = ''

    text = msg.reply_to_message.text
    # save as png
    img_path = sticker_from_text(user_id, username, text, avatar_path, msg_time, other_user_id)
    try:
        with open(img_path, 'rb') as png_sticker:
            bot.add_sticker_to_set(
                user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji
            )
            sticker = bot.get_sticker_set(pack_name).stickers[-1]
            msg.reply_sticker(sticker)
    except Exception as exc:
        if isinstance(exc, telegram.error.BadRequest):
            exception_msg = exc.message.lower()
            if exception_msg in responses.TELEGRAM_ERROR_CODES:
                msg.reply_text(responses.TELEGRAM_ERROR_CODES[exception_msg])
                return True
        logger.error(
            "Exception on add_text. User %s (id %d) Pack %s",
            username,
            user_id,
            pack_name,
        )
        logger.error(exc)
        return False
    finally:
        if os.path.exists(img_path):
            os.remove(img_path)
        if os.path.exists(avatar_path):
            os.remove(avatar_path)

    return True


def caption_handler(update: Update, context: CallbackContext):
    text = update.message.caption
    if text is None or text == '':
        return
    if text.split()[0] == '/addsticker':
        update.message.text = text
        add_sticker(context.bot, update)


def add_photo(bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str, replied: bool):
    if replied:
        photo = msg.reply_to_message.photo[-1]
    else:
        photo = msg.photo[-1]
    img_path = IMG_DIR / f'{IMG_PREFIX}{user_id}.jpg'
    try:
        bot.get_file(photo.file_id).download(custom_path=img_path)
        # resize and save as png
        img_path = sticker_from_image(img_path)
        with open(img_path, 'rb') as png_sticker:
            bot.add_sticker_to_set(
                user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji
            )
            sticker = bot.get_sticker_set(pack_name).stickers[-1]
            msg.reply_sticker(sticker)
    except Exception as exc:
        if isinstance(exc, telegram.error.BadRequest):
            exception_msg = exc.message.lower()
            if exception_msg in responses.TELEGRAM_ERROR_CODES:
                msg.reply_text(responses.TELEGRAM_ERROR_CODES[exception_msg])
                return True
        logger.error(
            "Exception on add_photo. User id %d Pack %s",
            user_id,
            pack_name,
        )
        logger.error(exc)
        return False

    return True


def add_document(bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str, replied: bool):
    if replied:
        doc = msg.reply_to_message.document
    else:
        doc = msg.document

    try:
        bot.add_sticker_to_set(
            user_id=user_id, name=pack_name, png_sticker=doc.file_id, emojis=emoji
        )
        sticker = bot.get_sticker_set(pack_name).stickers[-1]
        msg.reply_sticker(sticker)
    except telegram.error.BadRequest as exc:
        exception_msg = exc.message.lower()
        if exception_msg in responses.TELEGRAM_ERROR_CODES:
            msg.reply_text(responses.TELEGRAM_ERROR_CODES[exception_msg])
    except Exception:
        msg.reply_text(responses.INVALID_DOC)
        return False
    return True


def insert_sticker_in_pack(bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str):
    sticker_id = msg.reply_to_message.sticker.file_id

    img_path = IMG_DIR / f'{IMG_PREFIX}{user_id}.jpg'
    try:
        sticker_file = bot.get_file(sticker_id)
        sticker_file.download(custom_path=str(img_path))
        # resize and save as png
        img_path = sticker_from_image(img_path)
        with open(img_path, 'rb') as png_sticker:
            bot.add_sticker_to_set(
                user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji
            )
            sticker = bot.get_sticker_set(pack_name).stickers[-1]
            msg.reply_sticker(sticker)
    except Exception as exc:
        if isinstance(exc, telegram.error.BadRequest):
            exception_msg = exc.message.lower()
            if exception_msg in responses.TELEGRAM_ERROR_CODES:
                msg.reply_text(responses.TELEGRAM_ERROR_CODES[exception_msg])
                return True
        logger.error(
            "Exception inserting sticker in pack. User id %d Pack %s",
            user_id,
            pack_name,
        )
        logger.error(exc)
        return False
    return True


def del_sticker(update: Update, context: CallbackContext):
    bot = context.bot
    msg: Message = update.message
    msg_type = get_msg_type(msg)
    user_id = msg.from_user.id

    try:
        if msg_type == MsgType.TEXT:
            splittext = shlex.split(msg.text)
            title = splittext[1]
            pos = int(splittext[2])

            pack_name = build_pack_name(title, bot)
            sticker_id = bot.get_sticker_set(pack_name).stickers[pos].file_id
        elif msg_type == MsgType.REP_STICKER:
            pack_name = msg.reply_to_message.sticker.set_name
            sticker_id = msg.reply_to_message.sticker.file_id

        if pack_name is None:
            msg.reply_text('Não é possível remover o sticker de um pack inexistente.')
            return

        if not repository().check_permission(user_id, pack_name):
            msg.reply_text(responses.NO_PERMISSION)
            return

        bot.delete_sticker_from_set(sticker_id)
        msg.reply_text(responses.REMOVED_STICKER)

    except Exception:
        msg.reply_text(responses.REMOVE_STICKER_HELP)


def set_default_pack(update: Update, context: CallbackContext):
    bot = context.bot
    msg: Message = update.message
    user_id = msg.from_user.id

    if check_msg_format(msg.text):
        splittext = shlex.split(msg.text)
        title = splittext[1]
        pack_name = build_pack_name(title, bot)

        # check if user is pack's owner
        if repository().check_permission(user_id, pack_name):
            repository().users().get(user_id).def_pack = pack_name
        else:
            msg.reply_text(responses.NO_PERMISSION)
            return
    else:
        update.message.reply_text(responses.INVALID_MSG)


def handler_pack_public(update: Update, context: CallbackContext):
    _set_pack_public(update, context, True)


def handler_pack_private(update: Update, context: CallbackContext):
    _set_pack_public(update, context, False)


def _set_pack_public(update: Update, context: CallbackContext, is_public: bool):
    msg: Message = update.message
    user_id = msg.from_user.id

    if check_msg_format(msg.text):
        splittext = shlex.split(msg.text)
        title = splittext[1]
        pack_name = build_pack_name(title, context.bot)

        # check if user is pack's owner
        if repository().check_permission(user_id, pack_name):
            repository().set_pack_public(pack_name, is_public)
            msg.reply_text(responses.PACK_PRIVACY_UPDATED)
        else:
            msg.reply_text(responses.NO_PERMISSION)
            return
    else:
        msg.reply_text(responses.INVALID_MSG)


@creator_only
def add_pack_to_user(update: Update, context: CallbackContext):
    msg: Message = update.message
    try:
        user = msg.reply_to_message.forward_from
        if user is None:
            user = msg.reply_to_message.from_user

        if check_msg_format(msg.text):
            splittext = shlex.split(msg.text)
            title = splittext[1]
            pack_name = build_pack_name(title, context.bot)

            repository().add_pack_to_user(user, pack_name)
        else:
            msg.reply_text(responses.INVALID_MSG)
    except Exception:
        msg.reply_text(responses.ERROR_MSG)


def check_msg_format(text: str):
    return text is not None and len(text.split()) > 1


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
        msg_type = MsgType.TEXT

    if replied:
        return MsgType(msg_type * 10)
    else:
        return msg_type


def handler_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    update.message.reply_text(responses.HELP_MSG)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
