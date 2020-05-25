from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from login import login_required

from models import Keyword, Admin

from channels import channels

WORDS, ADD_WORDS, REMOVE_WORDS = range(1, 4)


@login_required
def keywords(update, context):
    context.user_data['keywords_dict'] = {}
    context.user_data['remove_keywords'] = []

    keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                 InlineKeyboardButton("حذف", callback_data='2')],
                [InlineKeyboardButton("خانه", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keywords = ""
    i = 1
    admin = Admin.get_by_username(update.effective_message.from_user.username)
    for keyword in Admin.get_keywords(admin.username):
        keywords += "{0}. {1} \n".format(i, keyword.name)
        context.user_data['keywords_dict'].update({i: keyword})
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
    try:
        keyword_sent_list = update.effective_message.text.split('\n')
    except ValueError:
        update.message.reply_text('ورودی اشتباه')
        return ADD_WORDS

    admin = Admin.get_by_username(update.effective_message.from_user.username)
    for keyword in keyword_sent_list:
        if not keyword in Admin.get_keywords(admin.username):
            Keyword(name=keyword, admin_id=admin.id).add()

    return ADD_WORDS


def remove_keywords_alert(update, context):
    update.callback_query.message.reply_text(
        'شماره واژه هایی که قصد حذف شان را دارید بفرستید سپس /done را ارسال کنید: ')
    return REMOVE_WORDS


def check_remove_keywords(update, context):
    try:
        index = int(update.message.text)
    except ValueError:
        update.message.reply_text('ورودی اشتباه')
        return REMOVE_WORDS
    keyword = context.user_data['keywords_dict'].get(index)
    if keyword:
        context.user_data['remove_keywords'].append(keyword)
    else:
        update.message.reply_text('واژه {} وجود ندارد'.format(index))
    return REMOVE_WORDS


def remove_keywords(update, context):
    remove = context.user_data['remove_keywords'][:]
    for keyword in remove:
        Keyword.delete(keyword)
        context.user_data['remove_keywords'].remove(keyword)
    return keywords(update, context)
