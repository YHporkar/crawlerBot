from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from crawler import get_channel_name

from login import login_required
import re

CHANNELS, ADD_CHANNELS, REMOVE_CHANNELS = range(4, 7)


@login_required
def channels(update, context):
    keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                 InlineKeyboardButton("حذف", callback_data='2'), ],
                [InlineKeyboardButton("خانه", callback_data='0')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    channels = ""
    i = 1
    for channel in context.user_data['channels']:
        channels += "{0}. {1} \n".format(i, channel['username'])
        i += 1
    update.message.reply_text(
        "کانال های شما: \n" + channels, reply_markup=reply_markup)
    return CHANNELS


def add_channels_alert(update, context):
    update.callback_query.message.reply_text(
        'آیدی کانال ها را نوشته و بفرستید')
    return ADD_CHANNELS


def add_channel(update, context):
    temp = update.message.reply_text('لطفا صبر کنید...')
    channel_sent_list = update.message.text.split('\n')
    channel_store_list = []
    for channel in context.user_data['channels']:
        channel_store_list.append(channel.get('username'))
    for username in channel_sent_list:
        if username.__contains__('t.me') or username.__contains__('telegram.me'):
            username = '@' + \
                re.search(r'\/\w{5,}', username).group(0).replace('/', '')
        if username not in channel_store_list:
            channel_name = get_channel_name(username)
            if channel_name:
                context.user_data['channels'].append(
                    {'username': username, 'channel_name': channel_name.get_text()})
            else:
                update.message.reply_text(
                    'کانال {} وجود ندارد'.format(username))
    update.message.bot.edit_message_text(
        chat_id=update.message.chat_id, message_id=temp.message_id, text='اکنون /done را برای ذخیره سازی کانال ها ارسال کنید')
    return ADD_CHANNELS


def remove_channels_alert(update, context):
    context.user_data['remove_channels'] = []
    update.callback_query.message.reply_text(
        'شماره کانال هایی که قصد حذف شان را دارید بفرستید سپس /done را ارسال کنید: ')
    return REMOVE_CHANNELS


def check_remove_channels(update, context):
    index = int(update.message.text)
    try:
        context.user_data['channels'][index - 1]
        context.user_data['remove_channels'].append(index - 1)
    except IndexError:
        update.message.reply_text('کانال {} وجود ندارد'.format(index))
    return REMOVE_WORDS


def remove_channels(update, context):
    for index in context.user_data['remove_channels']:
        context.user_data['channels'][index] = '$'

    context.user_data['channels'] = list(
        filter(lambda a: a != '$', context.user_data['channels']))

    return channels(update, context)
