from telegram.ext import Updater, CommandHandler  # , MessageHandler, Filters
import logging
import os

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text("Hi!")


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text("No! *runs away*")


def make_sticker(bot, update):
    message = "Ok, coloquei na lista"
    update.message.reply_text(message)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""

    token = os.environ.get("TOKEN")
    if not token:
        raise Exception("TOKEN enviroment variable not found")

    updater = Updater(token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("make_sticker", make_sticker))
    dp.add_handler(CommandHandler("help", help))

    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
