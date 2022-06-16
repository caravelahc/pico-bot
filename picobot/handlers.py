import logging
import os
import shlex
from functools import wraps
from pathlib import Path

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

        update.message.reply_text(responses.CREATOR_ACCESS_DENIED)
        return None

    return new_func


def build_pack_name(title: str, bot: Bot) -> str:
    slug = slugify(title, separator="_", lowercase=False)
    return f'{slug}_by_{bot.username}'


def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    if update.message is not None:
        update.message.reply_text(responses.GREETING)


def create_pack(update: Update, context: CallbackContext) -> None:
    bot = context.bot

    assert update.message is not None

    user = update.message.from_user

    assert user is not None

    text = update.message.text

    assert text is not None

    if text is None or not check_msg_format(text):
        update.message.reply_text(responses.INVALID_MSG)
        return

    splittext = shlex.split(text)

    title = splittext[1]
    name = build_pack_name(title, bot)
    emoji = splittext[2] if len(splittext) > 2 else DEFAULT_EMOJI

    # Create Pack
    try:
        with open(IMG_DIR / 'caravela.png', 'rb') as png_sticker:
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
        raise


def add_sticker(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    msg = update.message

    assert msg is not None

    user = msg.from_user

    assert user is not None
    assert msg.text is not None

    msg_type = get_msg_type(msg)
    response = responses.ERROR_MSG
    splittext = shlex.split(msg.text)

    if check_msg_format(msg.text):
        title = splittext[1]
        pack_name = build_pack_name(title, bot)

        # check if user is pack's owner
        if not repository().check_permission(user.id, pack_name):
            msg.reply_text(responses.NO_PERMISSION)
            return

    else:  # if pack name not informed check if user has default pack
        user_from_db = repository().users().get(user.id)

        if user_from_db is not None and user_from_db.def_pack is not None:
            pack_name = user_from_db.def_pack
        else:
            msg.reply_text(responses.INVALID_MSG)
            return

    if len(splittext) > 2:
        emoji = splittext[2]
    else:
        emoji = DEFAULT_EMOJI

    # check if it's image, file, text, or sticker
    if msg_type == MsgType.REP_TEXT:
        if add_text(bot, msg, user.id, pack_name, emoji):
            return
    elif msg_type == MsgType.PHOTO:
        if add_photo(bot, msg, user.id, pack_name, emoji, False):
            return
    elif msg_type == MsgType.REP_PHOTO:
        if add_photo(bot, msg, user.id, pack_name, emoji, True):
            return
    elif msg_type == MsgType.DOCUMENT:
        if add_document(bot, msg, user.id, pack_name, emoji, False):
            return
    elif msg_type == MsgType.REP_DOCUMENT:
        if add_document(bot, msg, user.id, pack_name, emoji, True):
            return
    elif msg_type in [MsgType.STICKER, MsgType.REP_STICKER]:
        if insert_sticker_in_pack(bot, msg, user.id, pack_name, emoji):
            return

    # check for errors

    msg.reply_text(response)


def add_text(bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str) -> bool:
    reply = msg.reply_to_message

    assert reply is not None

    forward = reply.forward_from

    if forward is not None:
        username = forward.first_name
        other_user_id = forward.id

        forward_date = reply.forward_date

        assert forward_date is not None

        msg_time = forward_date.strftime('%H:%M')
    else:
        from_user = reply.from_user

        assert from_user is not None

        username = from_user.first_name
        other_user_id = from_user.id
        msg_time = reply.date.strftime('%H:%M')

    user_profile_photos = bot.get_user_profile_photos(other_user_id, limit=1)

    assert user_profile_photos is not None

    text = reply.text

    assert text is not None

    photos = user_profile_photos.photos
    avatar_path = Path('')
    try:
        photo = photos[0][0]
        avatar_path = IMG_DIR / f'{AVATAR_PREFIX}{other_user_id}.jpg'
        bot.get_file(photo.file_id).download(custom_path=str(avatar_path))
    except Exception:  # pylint: disable=broad-except
        msg.reply_text(responses.ERROR_DOWNLOAD_PHOTO)
        avatar_path = Path('')

    # save as png
    img_path = sticker_from_text(user_id, username, text, str(avatar_path), msg_time, other_user_id)
    try:
        with open(img_path, 'rb') as png_sticker:
            bot.add_sticker_to_set(
                user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji
            )
            sticker = bot.get_sticker_set(pack_name).stickers[-1]
            msg.reply_sticker(sticker)
    except Exception as exc:  # pylint: disable=broad-except
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


def caption_handler(update: Update, context: CallbackContext) -> None:
    msg = update.message

    assert msg is not None

    text = msg.caption
    if text is None or text == '':
        return
    if text.split()[0] == '/addsticker':
        msg.text = text
        add_sticker(update, context)


def add_photo(
    bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str, replied: bool
) -> bool:
    if replied:
        reply = msg.reply_to_message

        assert reply is not None

        photo = reply.photo[-1]
    else:
        photo = msg.photo[-1]
    img_path = IMG_DIR / f'{IMG_PREFIX}{user_id}.jpg'
    try:
        bot.get_file(photo.file_id).download(custom_path=str(img_path))
        # resize and save as png
        img_path = sticker_from_image(img_path)
        with open(img_path, 'rb') as png_sticker:
            bot.add_sticker_to_set(
                user_id=user_id, name=pack_name, png_sticker=png_sticker, emojis=emoji
            )
            sticker = bot.get_sticker_set(pack_name).stickers[-1]
            msg.reply_sticker(sticker)
    except Exception as exc:  # pylint: disable=broad-except
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


def add_document(
    bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str, replied: bool
) -> bool:
    if replied:
        reply = msg.reply_to_message

        assert reply is not None

        doc = reply.document
    else:
        doc = msg.document

    assert doc is not None

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
    except Exception:  # pylint: disable=broad-except
        msg.reply_text(responses.INVALID_DOC)
        return False
    return True


def insert_sticker_in_pack(
    bot: Bot, msg: Message, user_id: int, pack_name: str, emoji: str
) -> bool:
    reply = msg.reply_to_message

    assert reply is not None

    sticker = reply.sticker

    assert sticker is not None

    sticker_id = sticker.file_id

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
    except Exception as exc:  # pylint: disable=broad-except
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


def del_sticker(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    msg = update.message

    assert msg is not None

    from_user = msg.from_user

    assert from_user is not None

    msg_type = get_msg_type(msg)
    user_id = from_user.id

    try:
        if msg_type == MsgType.TEXT:
            assert msg.text is not None

            splittext = shlex.split(msg.text)
            title = splittext[1]
            pos = int(splittext[2])

            pack_name = build_pack_name(title, bot)
            sticker_id = bot.get_sticker_set(pack_name).stickers[pos].file_id
        elif msg_type == MsgType.REP_STICKER:
            reply = msg.reply_to_message

            assert reply is not None

            sticker = reply.sticker

            assert sticker is not None
            assert sticker.set_name is not None

            pack_name = sticker.set_name
            sticker_id = sticker.file_id

        if pack_name is None:
            msg.reply_text('Não é possível remover o sticker de um pack inexistente.')
            return

        if not repository().check_permission(user_id, pack_name):
            msg.reply_text(responses.NO_PERMISSION)
            return

        bot.delete_sticker_from_set(sticker_id)
        msg.reply_text(responses.REMOVED_STICKER)

    except Exception:  # pylint: disable=broad-except
        msg.reply_text(responses.REMOVE_STICKER_HELP)


def set_default_pack(update: Update, context: CallbackContext) -> None:
    bot = context.bot
    msg = update.message

    assert msg is not None

    from_user = msg.from_user

    assert from_user is not None

    user_id = from_user.id

    text = msg.text

    assert text is not None

    if check_msg_format(text):
        splittext = shlex.split(text)
        title = splittext[1]
        pack_name = build_pack_name(title, bot)

        # check if user is pack's owner
        if repository().check_permission(user_id, pack_name):
            repository().users().get(user_id).def_pack = pack_name
        else:
            msg.reply_text(responses.NO_PERMISSION)
            return
    else:
        msg.reply_text(responses.INVALID_MSG)


def handler_pack_public(update: Update, context: CallbackContext):
    _set_pack_public(update, context, True)


def handler_pack_private(update: Update, context: CallbackContext):
    _set_pack_public(update, context, False)


def _set_pack_public(update: Update, context: CallbackContext, is_public: bool):
    msg = update.message

    assert msg is not None

    from_user = msg.from_user

    assert from_user is not None

    user_id = from_user.id

    text = msg.text

    assert text is not None

    if check_msg_format(text):
        splittext = shlex.split(text)
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
    msg = update.message

    assert msg is not None

    try:
        reply = msg.reply_to_message

        assert reply is not None

        user = reply.forward_from

        if user is None:
            user = reply.from_user

        text = msg.text

        assert text is not None

        if check_msg_format(text):
            splittext = shlex.split(text)
            title = splittext[1]
            pack_name = build_pack_name(title, context.bot)

            repository().add_pack_to_user(user, pack_name)
        else:
            msg.reply_text(responses.INVALID_MSG)
    except Exception:  # pylint: disable=broad-except
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

    return msg_type


def handler_help(update: Update, _: CallbackContext):
    """Send a message when the command /help is issued."""
    msg = update.message

    assert msg is not None

    msg.reply_text(responses.HELP_MSG)


def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
