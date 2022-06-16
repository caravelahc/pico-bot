from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from picobot import handlers
from picobot.config import DB_PATH, TOKEN
from picobot.repository.repo import repository


def main():
    """Start the bot."""

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_error_handler(handlers.error)

    dispatcher.add_handler(CommandHandler('start', handlers.start))
    dispatcher.add_handler(CommandHandler('addsticker', handlers.add_sticker))
    dispatcher.add_handler(CommandHandler('newpack', handlers.create_pack))
    dispatcher.add_handler(CommandHandler('delsticker', handlers.del_sticker))
    dispatcher.add_handler(CommandHandler('help', handlers.handler_help))
    dispatcher.add_handler(CommandHandler('setdefaultpack', handlers.set_default_pack))
    dispatcher.add_handler(CommandHandler('setpublic', handlers.handler_pack_public))
    dispatcher.add_handler(CommandHandler('setprivate', handlers.handler_pack_private))
    media_filter = (Filters.photo | Filters.document) & (~Filters.reply)
    dispatcher.add_handler(MessageHandler(filters=media_filter, callback=handlers.caption_handler))

    dispatcher.add_handler(CommandHandler('add_pack_to_user', handlers.add_pack_to_user))

    repository(DB_PATH)  # create or load persistence repository
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
