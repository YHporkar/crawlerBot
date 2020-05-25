from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from crawler import get_channel_name

from login import login_required
import re

from models import Channel, Admin

CHANNELS, ADD_CHANNELS, REMOVE_CHANNELS = range(4, 7)


@login_required
def channels(update, context):
    context.user_data['channels_dict'] = {}
    context.user_data['remove_channels'] = []

    if Admin.get_by_username(update.message.from_user.username).is_super:
        keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                     InlineKeyboardButton("حذف", callback_data='2')],
                    [InlineKeyboardButton("خانه", callback_data='0')]]
    else:
        keyboard = [[InlineKeyboardButton("افزودن", callback_data='1')],
                    [InlineKeyboardButton("خانه", callback_data='0')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    channels = ""
    i = 1
    for channel in Channel.get_all():
        channels += "{0}. {1} \n".format(i, channel.username)
        context.user_data['channels_dict'].update({i: channel})
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
    try:
        channel_sent_list = update.effective_message.text.split('\n')
    except ValueError:
        update.message.reply_text('ورودی اشتباه')
        return ADD_CHANNELS

    channel_store_list = []
    for channel in Channel.get_all():
        channel_store_list.append(channel.username)
    for username in channel_sent_list:
        if username.__contains__('t.me') or username.__contains__('telegram.me'):
            username = '@' + \
                re.search(r'\/\w{5,}', username).group(0).replace('/', '')
        if username not in channel_store_list:
            channel_name = get_channel_name(username)
            if channel_name:
                Channel(username=username, name=channel_name.get_text()).add()
            else:
                update.message.reply_text(
                    'کانال {} وجود ندارد'.format(username))
    update.message.bot.edit_message_text(
        chat_id=update.message.chat_id, message_id=temp.message_id, text='اکنون /done را برای ذخیره سازی کانال ها ارسال کنید')
    return ADD_CHANNELS


def remove_channels_alert(update, context):
    update.callback_query.message.reply_text(
        'شماره کانال هایی که قصد حذف شان را دارید بفرستید سپس /done را ارسال کنید: ')
    return REMOVE_CHANNELS


def check_remove_channels(update, context):
    try:
        index = int(update.effective_message.text)
    except ValueError:
        update.message.reply_text('ورودی اشتباه')
        return REMOVE_CHANNELS

    channel = context.user_data['channels_dict'].get(index)
    if channel:
        context.user_data['remove_channels'].append(channel)
    else:
        update.message.reply_text('کانال {} وجود ندارد'.format(index))
    return REMOVE_CHANNELS


def remove_channels(update, context):
    remove = context.user_data['remove_channels'][:]
    for channel in remove:
        Channel.delete(channel)
        context.user_data['remove_channels'].remove(channel)
    return channels(update, context)


# def remove_all_channels(update, context):
#     for channel in Channel.get_all():
#         Channel.delete(channel)
#     return channels(update.callback_query, context)
