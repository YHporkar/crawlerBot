import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler,
                          CallbackQueryHandler)

from config import token

from models import Admin, Base, engine, Keyword

from process import *
from keywords import *
from channels import *
from admins import *
from login import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


SELECTING_ACTION = 0

start_keyboard = [['واژه ها', 'کانال ها'], ['شروع جستجو']]
start_markup = ReplyKeyboardMarkup(start_keyboard, resize_keyboard=True)


@login_required
def start(update, context):
    admin = Admin.get_by_username(username=update.message.from_user.username)
    context.user_data['is_super'] = admin.is_super
    if admin.is_super:
        update.message.reply_text(
            'لطفا انتخاب کنید.\nبرای ورود به بخش مدیریت /admin را بفرستید', reply_markup=start_markup)
    else:
        update.message.reply_text(
            'لطفا انتخاب کنید', reply_markup=start_markup)

    return SELECTING_ACTION


def end_features(update, context):
    if context.user_data['is_super']:
        update.callback_query.message.reply_text(
            'لطفا انتخاب کنید.\nبرای ورود به بخش مدیریت /admin را بفرستید', reply_markup=start_markup)
    else:
        update.callback_query.message.reply_text(
            'لطفا انتخاب کنید', reply_markup=start_markup)
    return SELECTING_ACTION


def home(update, context):
    if not update.message:
        update = update.callback_query
    if context.user_data['is_super']:
        update.message.reply_text(
            'لطفا انتخاب کنید.\nبرای ورود به بخش مدیریت /admin را بفرستید', reply_markup=start_markup)
    else:
        update.message.reply_text(
            'لطفا انتخاب کنید', reply_markup=start_markup)
    context.user_data['all_posts'] = []

    # remove all keywords
    for keyword in Keyword.get_all():
        Keyword.delete(keyword)

    return SELECTING_ACTION


def access_denied(update, context):
    update.message.reply_text('دسترسی مقدور نیست')


def error(update, context, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def bot():
    updater = Updater(token, use_context=True)
    dp = updater.dispatcher

    words_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex('واژه ها'), keywords)],

        states={
            WORDS: [CallbackQueryHandler(add_keywords_alert, pattern=r'1'),
                    CallbackQueryHandler(remove_keywords_alert, pattern=r'2')],
            ADD_WORDS: [MessageHandler(Filters.regex(r'[ شسیبلاتنمکگضصثقفغعهخحجچپظطزرذدئو,]+'), add_keywords),
                        CommandHandler('done', keywords)],
            REMOVE_WORDS: [MessageHandler(Filters.regex(r'[0-9]+'), check_remove_keywords),
                           CommandHandler('done', remove_keywords)]
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
            ADD_CHANNELS: [MessageHandler(Filters.regex(r'(https:\/\/t\.me\/\w+ ?| ?@\w{5,})'), add_channel),
                           CommandHandler('done', channels)],
            REMOVE_CHANNELS: [MessageHandler(Filters.regex(r'[0-9]+'), check_remove_channels),
                              CommandHandler('done', remove_channels)]
            #   @\w{5,} |
        },
        fallbacks=[CallbackQueryHandler(end_features, pattern=r'0')],
        map_to_parent={
            SELECTING_ACTION: SELECTING_ACTION
        }
    )

    admins_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', admins)],
        states={
            ADMINS: [CallbackQueryHandler(add_admins_alert, pattern=r'1'),
                     CallbackQueryHandler(remove_admins_alert, pattern=r'2')],
            ADD_ADMINS: [MessageHandler(Filters.regex(r'@\w{5,}'), add_admins),
                         CommandHandler('done', admins)],
            REMOVE_ADMINS: [MessageHandler(Filters.regex(r'[0-9]+'), check_remove_admins),
                            CommandHandler('done', remove_admins)]
        },
        fallbacks=[CallbackQueryHandler(end_features, pattern=r'0')],
        map_to_parent={
            SELECTING_ACTION: SELECTING_ACTION
        }
    )

    process_handler = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex('شروع جستجو'), start_process)],
        states={
            SET_DATE: [CallbackQueryHandler(manually_date_alert, pattern=r'4'),
                       CallbackQueryHandler(choosen_date, pattern=r'1|2|3'),
                       MessageHandler(Filters.regex(
                           r'[0-9]{4}-[0-9]{2}-[0-9]{2}'), manually_date),
                       MessageHandler(~ Filters.regex(r'[0-9]{4}-[0-9]{2}-[0-9]{2}'), wrong_date)],

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
                               words_handler,
                               admins_handler],

            # NOTREGISTERED: [MessageHandler(Filters.all, access_denied)]
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
    Base.metadata.create_all(engine)
    # Admin.initialize()
    bot()
