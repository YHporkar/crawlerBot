from telegram import InlineKeyboardButton, InlineKeyboardMarkup


CHANNELS, ADD_CHANNELS, REMOVE_CHANNELS = range(4, 7)


def channels(update, context):
    keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                 InlineKeyboardButton("حذف", callback_data='2'), ],
                [InlineKeyboardButton("خانه", callback_data='0')]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    channels = ""
    i = 1
    for channel in context.user_data['channels']:
        channels += "{0}. {1} \n".format(i, '@'+channel['username'])
        i += 1
    update.message.reply_text(
        "کانال های شما: \n\n" + channels, reply_markup=reply_markup)
    return CHANNELS


def add_channels_alert(update, context):
    update.callback_query.message.reply_text(
        'پست آخر کانال را فوروارد کنید سپس /done را ارسال کنید')
    return ADD_CHANNELS


def add_channel(update, context):
    message = update.message
    channel_username = message.forward_from_chat.username
    start = message.forward_from_message_id
    channel_name = message.forward_from_chat.title
    channel_list = []
    for channel in context.user_data['channels']:
        channel_list.append(channel.get('username'))
    if channel_username not in channel_list:
        context.user_data['channels'].append(
            {'username': channel_username, 'channel_name': channel_name, 'start': start})

    return ADD_CHANNELS


def remove_channels_alert(update, context):
    update.callback_query.message.reply_text(
        'شماره کانال هایی که قصد حذف شان را دارید بفرستید سپس /done را بفرستید: ')
    return REMOVE_CHANNELS


def remove_channel(update, context):
    index = int(update.message.text)
    try:
        del context.user_data['channels'][index - 1]
    except ValueError:
        update.message.reply_text('این کانال وجود ندارد')
    return REMOVE_CHANNELS


def channel_callback(update, context):
    update.message.reply_text('یکی از گزینه های موجود را انتخاب کنید')
