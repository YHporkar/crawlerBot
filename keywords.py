from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from login import login_required


WORDS, ADD_WORDS, REMOVE_WORDS = range(1, 4)


@login_required
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
        "واژه های شما: \n" + keywords, reply_markup=reply_markup)
    return WORDS


def add_keywords_alert(update, context):
    update.callback_query.message.reply_text(
        "واژه های خود را بفرستید سپس /done را ارسال کنید: \n"
        "برای اینکه وجود چند واژه باهم در یک کپشن را تعیین کنید بین هر واژه از علامت ',' استفاده کنید\n\n"
        "مثال: واژه1,واژه2")
    return ADD_WORDS


def add_keywords(update, context):
    keyword_sent_list = update.message.text.split('\n')
    for keyword in keyword_sent_list:
        if not keyword in context.user_data['keywords']:
            context.user_data['keywords'].append(keyword)

    return ADD_WORDS


def remove_keywords_alert(update, context):
    context.user_data['remove_keywords'] = []
    update.callback_query.message.reply_text(
        'شماره واژه هایی که قصد حذف شان را دارید بفرستید سپس /done را ارسال کنید: ')
    return REMOVE_WORDS


def check_remove_keywords(update, context):
    index = int(update.message.text)
    try:
        context.user_data['keywords'][index - 1]
        context.user_data['remove_keywords'].append(index - 1)
    except IndexError:
        update.message.reply_text('واژه {} وجود ندارد'.format(index))
    return REMOVE_WORDS


def remove_keywords(update, context):
    for index in context.user_data['remove_keywords']:
        context.user_data['keywords'][index] = '$'

    context.user_data['keywords'] = list(
        filter(lambda a: a != '$', context.user_data['keywords']))

    return keywords(update, context)
