from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from crawler import get_channel_name

from login import login_required
import re
import math

from models import Channel, Admin

CHANNELS, ADD_CHANNELS, REMOVE_CHANNELS = range(4, 7)


super_keyboard = [[InlineKeyboardButton("صفحه قبل", callback_data='3'),
                   InlineKeyboardButton("صفحه بعد", callback_data='4')],
                  [InlineKeyboardButton("افزودن", callback_data='1'),
                   InlineKeyboardButton("حذف", callback_data='2')],
                  [InlineKeyboardButton("خانه", callback_data='0')]]

normal_keyboard = [[InlineKeyboardButton("صفحه قبل", callback_data='3'),
                    InlineKeyboardButton("صفحه بعد", callback_data='4')],
                   [InlineKeyboardButton("افزودن", callback_data='1')],
                   [InlineKeyboardButton("خانه", callback_data='0')]]


# @login_required
def channels(update, context):
    context.user_data['channels_dict'] = {}
    context.user_data['remove_channels'] = []

    if Admin.get_by_username(update.message.from_user.username).is_super:
        keyboard = super_keyboard
    else:
        keyboard = normal_keyboard

    context.user_data['channel_reply_markup'] = InlineKeyboardMarkup(keyboard)
    cp = context.user_data['current_channel_page'] = 1
    channels = Channel.get_all()[(cp-1)*25:cp*25]
    return show(update, context, channels)


def next_channels(update, context):
    query = update.callback_query
    if context.user_data['current_channel_page'] == math.ceil(len(Channel.get_all()) / 25):
        query.answer('صفحه بعد وجود ندارد')
    else:
        query.answer()
        context.user_data['current_channel_page'] += 1
        cp = context.user_data['current_channel_page']
        channels = Channel.get_all()[(cp-1)*25:cp*25]
        return show(update, context, channels)


def prev_channels(update, context):
    query = update.callback_query
    if context.user_data['current_channel_page'] == 1:
        query.answer('صفحه قبل وجود ندارد')
    else:
        query.answer()
        context.user_data['current_channel_page'] -= 1
        cp = context.user_data['current_channel_page']
        channels = Channel.get_all()[(cp-1)*25:cp*25]
        return show(update, context, channels)


def show(update, context, channels):
    current_page = context.user_data['current_channel_page']
    pages = math.ceil(len(Channel.get_all()) / 25)
    show_channels = ""
    i = 1
    for channel in channels:
        show_channels += "{0}. {1} \n".format(i, channel.username)
        context.user_data['channels_dict'].update({i: channel})
        i += 1
    text = "تعداد کانال ها: {0} | "\
        "صفحه {1} از {2}\n"\
        "کانال های موجود: \n".format(
            len(Channel.get_all()), current_page, pages) + show_channels

    reply_markup = context.user_data['channel_reply_markup']
    if not update.message:
        update = update.callback_query
        update.edit_message_text(
            text, reply_markup=reply_markup)
    else:
        update.message.reply_text(
            text, reply_markup=reply_markup)
    return CHANNELS


def add_channels_alert(update, context):
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        "آیدی کانال ها را نوشته و بفرستید\n"
        "بطور مثال میتوانید کانال ها را به صورت های زیر ارسال کنید:\n"
        "@username\n"
        "https://t.me/username/12345")
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
            try:
                username = '@' + \
                    re.search(r'\/\w{5,}', username).group(0).replace('/', '')
            except Exception:
                continue
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
    update.callback_query.answer()
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
