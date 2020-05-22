from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from models import Admin

ADMINS, ADD_ADMINS, REMOVE_ADMINS = range(1, 4)


def admins(update, context):
    keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                 InlineKeyboardButton("حذف", callback_data='2')],
                [InlineKeyboardButton("خانه", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    admins = ""
    i = 1
    context.user_data['admins'] = Admin.get_all()

    for admin in context.user_data['admins']:
        admins += "{0}. {1} \n".format(i, '@'+admin.username)
        i += 1
    update.message.reply_text(
        "ادمین ها: \n" + admins, reply_markup=reply_markup)
    return ADMINS


def add_admins_alert(update, context):
    update.callback_query.message.reply_text(
        'نام های کاربری را بفرستید سپس /done را ارسال کنید')
    return ADD_ADMINS


def add_admins(update, context):
    admin_sent_list = update.message.text.split('\n')
    for admin in admin_sent_list:
        if not admin in context.user_data['admins']:
            Admin(username=admin.replace('@', '')).add()

    return ADD_ADMINS


def remove_admins_alert(update, context):
    context.user_data['remove_admins'] = []
    update.callback_query.message.reply_text(
        'شماره ادمین هایی که قصد حذف شان را دارید بفرستید سپس /done را ارسال کنید: ')
    return REMOVE_ADMINS


def check_remove_admins(update, context):
    index = int(update.message.text)
    try:
        context.user_data['remove_admins'].append(
            context.user_data['admins'][index - 1])
    except IndexError:
        update.message.reply_text('ادمین {} وجود ندارد'.format(index))
    return REMOVE_ADMINS


def remove_admins(update, context):
    for admin in context.user_data['remove_admins']:
        Admin.delete(admin)

    return admins(update, context)
