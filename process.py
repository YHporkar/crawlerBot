from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import math
from datetime import datetime, timedelta
from crawler import get_matched_posts

from bot import SELECTING_ACTION, start_markup

SET_DATE, GET_POSTS = range(7, 9)


def start_process(update, context):
    if context.user_data['keywords'] == []:
        update.message.reply_text(
            'you dont have any keyword to search. add some')
        return SELECTING_ACTION
    if context.user_data['channels'] == []:
        update.message.reply_text(
            'you dont have any channel to search. add some')
        return SELECTING_ACTION

    keyboard = [[InlineKeyboardButton("today", callback_data='1'),
                 InlineKeyboardButton("yesterday", callback_data='2')],

                [InlineKeyboardButton(
                    "the day before yesterday", callback_data='3')],
                [InlineKeyboardButton("set manually", callback_data='4')],
                [InlineKeyboardButton("home", callback_data='0')]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)

    return SET_DATE


def manually_date_alert(update, context):
    update.callback_query.message.reply_text(
        'send the date in this format: Year-Month-Day')
    return SET_DATE


def manually_date(update, context):
    date = datetime.strptime(update.message.text, '%Y-%m-%d').date()
    update.message.reply_text('wait...')

    return get_posts(update, context, date)


def choosen_date(update, context):
    data = update.callback_query.data
    date = ''
    if data == '1':
        date = datetime.today().date()
    elif data == '2':
        date = (datetime.today() - timedelta(days=1)).date()
    elif data == '3':
        date = (datetime.today() - timedelta(days=2)).date()
    update.callback_query.message.reply_text('wait...')

    return get_posts(update.callback_query, context, date)


def get_posts(update, context, date):
    context.user_data['all_posts'] = []
    for channel in context.user_data['channels']:
        for post in get_matched_posts(channel, context.user_data['keywords'], date):
            context.user_data['all_posts'].append(post)
    context.user_data['posts_count'] = len(context.user_data['all_posts'])
    return next_posts(update, context)
    # context.user_data['count'] = len(all_posts)
    # update.message.reply_text('{} posts found'.format(
    #     len(context.user_data['all_posts'])))


def next_posts(update, context):
    keyboard = [[InlineKeyboardButton(
        "home and reset", callback_data='5'), InlineKeyboardButton("next", callback_data='1')]]

    try:
        update = update.callback_query
    except AttributeError:
        pass

    reply_markup = InlineKeyboardMarkup(keyboard)
    count = len(context.user_data['all_posts'])
    pages = math.ceil(context.user_data['posts_count'] / 5)

    if count == 0:
        update.message.reply_text('0 post found', reply_markup=start_markup)
        return SELECTING_ACTION
    if count <= 5:
        for post in context.user_data['all_posts'][0:count]:
            current_page = pages - int(count/5)
            update.message.reply_text(
                prettify(post), parse_mode=ParseMode.MARKDOWN)
            context.user_data['all_posts'] = []
        update.message.reply_text("{0} posts found \n\n"
                                  "page {1} of {2} \n\n"
                                  "{3}-{4}".format(
                                      context.user_data['posts_count'], current_page+1, pages,  current_page*5, (current_page + 1)*5))
        update.message.reply_text('choose: ', reply_markup=start_markup)
        return SELECTING_ACTION
    else:
        for post in context.user_data['all_posts'][0:5]:
            current_page = pages - int(count/5)
            update.message.reply_text(
                prettify(post), parse_mode=ParseMode.MARKDOWN)
        context.user_data['all_posts'] = context.user_data['all_posts'][5:]
        update.message.reply_text("{0} posts found \n\n"
                                  "page {1} of {2} \n\n"
                                  "{3} - {4}".format(
                                      context.user_data['posts_count'], current_page+1, pages, current_page*5, (current_page + 1)*5), reply_markup=reply_markup)
        return GET_POSTS


def prettify(post):
    prettier = "channel name: {0} \n"\
        "post link: [link]({1}) \n"\
        "caption: \n {2} \n".format(
            post['channel_name'], post['url'], post['caption'])
    return prettier
