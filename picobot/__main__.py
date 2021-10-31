from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from picobot import handlers

from picobot.config import DB_PATH, TOKEN
from picobot.repository.repo import repository


def main():
    """Start the bot."""

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_error_handler(handlers.error)

    dp.add_handler(CommandHandler('start', handlers.start))
    dp.add_handler(CommandHandler('addsticker', handlers.add_sticker))
    dp.add_handler(CommandHandler('newpack', handlers.create_pack))
    dp.add_handler(CommandHandler('delsticker', handlers.del_sticker))
    dp.add_handler(CommandHandler('help', handlers.handler_help))
    dp.add_handler(CommandHandler('setdefaultpack', handlers.set_default_pack))
    dp.add_handler(CommandHandler('setpublic', handlers.handler_pack_public))
    dp.add_handler(CommandHandler('setprivate', handlers.handler_pack_private))
    dp.add_handler(CommandHandler('change_emojis',handlers.change_emojis))
    media_filter = (Filters.photo | Filters.document) & (~Filters.reply)
    dp.add_handler(MessageHandler(filters=media_filter, callback=handlers.caption_handler))

    dp.add_handler(CommandHandler('add_pack_to_user', handlers.add_pack_to_user))

    repository(DB_PATH)  # create or load persistence repository
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
