from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from models import Admin

from login import login_required, super_login_required


ADMINS, ADD_ADMINS, REMOVE_ADMINS = range(1, 4)


@super_login_required
def admins(update, context):
    context.user_data['admins_dict'] = {}
    context.user_data['remove_admins'] = []

    keyboard = [[InlineKeyboardButton("افزودن", callback_data='1'),
                 InlineKeyboardButton("حذف", callback_data='2')],
                [InlineKeyboardButton("خانه", callback_data='0')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    admins = ""
    i = 1

    for admin in Admin.get_all():
        admins += "{0}. {1} \n".format(i, '@'+admin.username)
        context.user_data['admins_dict'].update({i: admin})
        i += 1
    update.message.reply_text(
        "ادمین ها: \n" + admins, reply_markup=reply_markup)
    return ADMINS


def add_admins_alert(update, context):
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        'نام های کاربری را بفرستید سپس /done را ارسال کنید')
    return ADD_ADMINS


def add_admins(update, context):
    try:
        admin_sent_list = update.effective_message.text.split('\n')
    except ValueError:
        update.message.reply_text('ورودی اشتباه')
        return ADD_ADMINS

    for admin in admin_sent_list:
        if not admin in context.user_data['admins_dict'].values():
            if admin.__contains__('0'):
                Admin(username=admin.replace(
                    '@', '').replace(' 0', ''), is_super=True).add()
            else:
                Admin(username=admin.replace('@', '')).add()

    return ADD_ADMINS


def remove_admins_alert(update, context):
    update.callback_query.answer()
    update.callback_query.message.reply_text(
        'شماره ادمین هایی که قصد حذف شان را دارید بفرستید سپس /done را ارسال کنید: ')
    return REMOVE_ADMINS


def check_remove_admins(update, context):
    try:
        index = int(update.effective_message.text)
    except ValueError:
        update.message.reply_text('ورودی اشتباه')
        return REMOVE_ADMINS

    admin = context.user_data['admins_dict'].get(index)
    if admin:
        context.user_data['remove_admins'].append(admin)
    else:
        update.message.reply_text('ادمین {} وجود ندارد'.format(index))
    return REMOVE_ADMINS


def remove_admins(update, context):
    for admin in context.user_data['remove_admins']:
        Admin.delete(admin)
        context.user_data['remove_admins'].remove(admin)
    return admins(update, context)
