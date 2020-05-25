from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.error import BadRequest


import math
from datetime import datetime, timedelta
from crawler import get_matched_posts, get_last_post_url

from bot import SELECTING_ACTION, start_markup, home

from persiantools.jdatetime import JalaliDate

from login import login_required

from models import Channel, Admin

SET_DATE, GET_POSTS = range(7, 9)


@login_required
def start_process(update, context):
    context.user_data['me'] = Admin.get_by_username(
        update.message.from_user.username)
    if Admin.get_keywords(Admin.get_by_username(update.message.from_user.username).username) == []:
        update.message.reply_text(
            'شما ابتدا باید برای جستجو کلید واژه ای تعیین کنید')
        return SELECTING_ACTION
    if Channel.get_all() == []:
        update.message.reply_text(
            'شما ابتدا باید برای جستجو کانالی تعیین کنید')
        return SELECTING_ACTION

    keyboard = [[InlineKeyboardButton("امروز", callback_data='1'),
                 InlineKeyboardButton("دیروز", callback_data='2')],

                [InlineKeyboardButton(
                    "2 روز پیش", callback_data='3')],
                [InlineKeyboardButton("ورود دستی تاریخ", callback_data='4')],
                [InlineKeyboardButton("بازگشت به خانه", callback_data='0')]
                ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        'از هم اکنون تا چه زمانی جستجو انجام شود؟', reply_markup=reply_markup)

    return SET_DATE


def manually_date_alert(update, context):
    update.callback_query.edit_message_text(
        " تاریخ را با فرمت زیر ارسال کنید \n\n"
        "روز-ماه-سال\n"
        "مثال: 05-02-1399")
    return SET_DATE


def manually_date(update, context):
    persian_date = list(map(int, update.effective_message.text.split('-')))
    try:
        date = JalaliDate(persian_date[0], persian_date[1],
                          persian_date[2]).to_gregorian()
    except ValueError:
        update.message.reply_text('تاریخ را درست وارد کنید')
        return SET_DATE
    update.message.reply_text('لطفا صبر کنید...')

    return get_posts(update, context, date)


def wrong_date(update, context):
    update.message.reply_text('تاریخ را درست وارد کنید')
    return SET_DATE


def choosen_date(update, context):
    data = update.callback_query.data
    date = ''
    if data == '1':
        date = datetime.today().date()
    elif data == '2':
        date = (datetime.today() - timedelta(days=1)).date()
    elif data == '3':
        date = (datetime.today() - timedelta(days=2)).date()
    update.callback_query.edit_message_text('لطفا صبر کنید...')

    return get_posts(update.callback_query, context, date)


def get_posts(update, context, date):
    context.user_data['all_posts'] = []
    for channel in Channel.get_all():

        Channel.update_start(channel, get_last_post_url(channel.username))

        for post in get_matched_posts(channel, Admin.get_keywords(context.user_data['me'].username), date):
            context.user_data['all_posts'].append(post)
    context.user_data['posts_count'] = len(context.user_data['all_posts'])
    return next_posts(update, context)
    # context.user_data['count'] = len(all_posts)
    # update.message.reply_text('{} posts found'.format(
    #     len(context.user_data['all_posts'])))


def next_posts(update, context):
    keyboard = [[InlineKeyboardButton(
        "ریست و بازگشت به خانه", callback_data='5'), InlineKeyboardButton("صفحه بعد", callback_data='1')]]

    if not update.message:
        update = update.callback_query

    count = len(context.user_data['all_posts'])
    pages = math.ceil(context.user_data['posts_count'] / 5)

    if count == 0:
        update.message.reply_text(
            'متأسفانه پستی یافت نشد', reply_markup=start_markup)
        return home(update, context)
    elif count <= 5:
        show_count = count
        show_posts(show_count, start_markup, pages, count, update, context)
        return home(update, context)
    elif count > 5:
        show_posts(5, InlineKeyboardMarkup(keyboard),
                   pages, count, update, context)
        return GET_POSTS


def show_posts(show_count, reply_markup, pages, count, update, context):
    if count < 5:
        current_page = pages - int(count/5)
        last = context.user_data['posts_count']
    elif count % 5 == 0:
        current_page = pages - int(count/5) + 1
        last = context.user_data['posts_count']
    else:
        current_page = pages - int(count/5)
        last = current_page*5
    for post in context.user_data['all_posts'][0:show_count]:
        try:
            update.message.reply_text(
                prettify(post), parse_mode=ParseMode.MARKDOWN)
        except BadRequest:
            continue
    context.user_data['all_posts'] = context.user_data['all_posts'][show_count:]
    update.message.reply_text("{0} پست یافت شد \n\n"
                              "صفحه {1} از {2} \n\n"
                              "شماره های {3} تا {4}".format(
                                  context.user_data['posts_count'], current_page, pages, (current_page-1)*5 + 1, last), reply_markup=reply_markup)


def prettify(post):
    prettier = "📢 {0} \n\n"\
        "🔗 [مشاهده پست در کانال]({1}) \n\n"\
        "👁‍🗨 تعداد بازدید: {2} \n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"\
        "💬 کپشن: \n {3} \n\n".format(
            post['channel_name'], post['url'], post['views'], post['caption'])
    return prettier
