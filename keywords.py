from telegram import InlineKeyboardButton, InlineKeyboardMarkup

WORDS, ADD_WORDS, REMOVE_WORDS = range(1, 4)


def keywords(update, context):
    keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                 InlineKeyboardButton("حذف", callback_data='2')],
                [InlineKeyboardButton("خانه", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keywords = ""
    i = 1
    for keyword in context.user_data['keywords']:
        keywords += "{0}. {1} \n".format(i, keyword)
        i += 1
    update.message.reply_text(
        "واژه های شما: \n\n" + keywords, reply_markup=reply_markup)
    return WORDS


def add_keywords_alert(update, context):
    update.callback_query.message.reply_text(
        'واژه های خود را بفرستید سپس /done را بفرستید: ')
    return ADD_WORDS


def add_keywords(update, context):
    context.user_data['keywords'].append(update.message.text)
    return ADD_WORDS


def remove_keywords_alert(update, context):
    update.callback_query.message.reply_text(
        'شماره واژه هایی که قصد حذف شان را دارید بفرستید سپس /done را بفرستید: ')
    return REMOVE_WORDS


def remove_keywords(update, context):
    index = int(update.message.text)
    print(context.user_data['keywords'])
    try:
        del context.user_data['keywords'][index - 1]
    except ValueError:
        update.message.reply_text('این واژه وجود ندارد')
    return REMOVE_WORDS


def word_callback(update, context):
    update.message.reply_text('یکی از گزینه های موجود را انتخاب کنید')
