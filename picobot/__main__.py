from telegram.ext import Updater, CommandHandler  # , MessageHandler, Filters

from picobot import handlers
from .config import TOKEN


def main():
    """Start the bot."""

    updater = Updater(TOKEN)

    dp = updater.dispatcher

    dp.add_error_handler(handlers.error)

    dp.add_handler(CommandHandler('start', handlers.start))
    dp.add_handler(CommandHandler('addsticker', handlers.add_sticker))
    dp.add_handler(CommandHandler('newpack', handlers.create_pack))
    dp.add_handler(CommandHandler('help', handlers.handler_help))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
