import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,
                          CallbackQueryHandler)

from config import token

from process import *
from keywords import *
from channels import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


SELECTING_ACTION = 0

start_keyboard = [['واژه ها', 'کانال ها'], ['شروع پردازش']]
start_markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)


def start(update, context):
    update.message.reply_text('choose: ', reply_markup=start_markup)
    context.user_data['keywords'] = []
    context.user_data['channels'] = []

    return SELECTING_ACTION


def end_features(update, context):
    try:
        update.message.reply_text('choose: ', reply_markup=start_markup)
    except AttributeError:
        update.callback_query.message.reply_text(
            'choose: ', reply_markup=start_markup)
    return SELECTING_ACTION


def home(update, context):
    update.callback_query.message.reply_text(
        'choose: ', reply_markup=start_markup)
    context.user_data['all_posts'] = []
    return SELECTING_ACTION


def error(update, context, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def bot():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    words_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('واژه ها'), keywords)],

        states={
            WORDS: [CallbackQueryHandler(add_keywords_alert, pattern=r'1'),
                    CallbackQueryHandler(remove_keywords_alert, pattern=r'2'),
                    ],
            ADD_WORDS: [MessageHandler(Filters.regex(r'[ شسیبلاتنمکگضصثقفغعهخحجچپظطزرذدئو]+'), add_keywords),
                        CommandHandler('done', keywords)],
            REMOVE_WORDS: [MessageHandler(Filters.regex(r'[0-9]+'), remove_keywords),
                           CommandHandler('done', keywords)]
        },
        fallbacks=[CallbackQueryHandler(end_features, pattern=r'0')],
        map_to_parent={
            SELECTING_ACTION: SELECTING_ACTION
        }
    )

    channels_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('کانال ها'), channels)],
        states={
            CHANNELS: [CallbackQueryHandler(add_channels_alert, pattern=r'1'),
                       CallbackQueryHandler(remove_channels_alert, pattern=r'2')],
            ADD_CHANNELS: [MessageHandler(Filters.forwarded, add_channel),
                           CommandHandler('done', channels)],
            REMOVE_CHANNELS: [MessageHandler(Filters.regex(r'[0-9]+'), remove_channel),
                              CommandHandler('done', channels)]
        },
        fallbacks=[CallbackQueryHandler(end_features, pattern=r'0')],
        map_to_parent={
            SELECTING_ACTION: SELECTING_ACTION
        }
    )

    process_handler = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex('شروع پردازش'), start_process)],
        states={
            SET_DATE: [CallbackQueryHandler(manually_date_alert, pattern=r'4'),
                       CallbackQueryHandler(choosen_date, pattern=r'1|2|3'),
                       MessageHandler(Filters.regex(r'[0-9]{4}-[0-9]{2}-[0-9]{2}'), manually_date)],

            GET_POSTS: [CallbackQueryHandler(next_posts, pattern=r'1')]
        },
        fallbacks=[CallbackQueryHandler(end_features, pattern=r'0'),
                   CallbackQueryHandler(home, pattern=r'5')],
        map_to_parent={
            SELECTING_ACTION: SELECTING_ACTION
        }
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            SELECTING_ACTION: [process_handler,
                               channels_handler,
                               words_handler],

            # NOTREGISTERED: [MessageHandler(Filters.all, access_denied)],

            # C_ADMIN: [MessageHandler(Filters.regex(r'@[A-Za-z0-9]+'), create_admin),
            #           # MessageHandler(~ Filters.regex(r"@[A-Za-z0-9]+"), wrong_username)
            #           ]
        },
        fallbacks=[
            CommandHandler('cancel', start)
        ]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    bot()
