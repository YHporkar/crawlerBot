from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
import math
from datetime import datetime, timedelta
from crawler import get_matched_posts, get_last_post_url

from bot import SELECTING_ACTION, start_markup

from persiantools.jdatetime import JalaliDate

from login import login_required

SET_DATE, GET_POSTS = range(7, 9)


@login_required
def start_process(update, context):
    if context.user_data['keywords'] == []:
        update.message.reply_text(
            'شما ابتدا باید برای جستجو کلید واژه ای تعیین کنید')
        return SELECTING_ACTION
    if context.user_data['channels'] == []:
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
    persian_date = list(map(int, update.message.text.split('-')))
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

    for channel in context.user_data['channels']:

        channel.update({'start': get_last_post_url(channel.get('username'))})

        for post in get_matched_posts(channel, context.user_data['keywords'], date):
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

    reply_markup = InlineKeyboardMarkup(keyboard)
    count = len(context.user_data['all_posts'])
    pages = math.ceil(context.user_data['posts_count'] / 5)

    if count % 5 == 0:
        current_page = pages - int(count/5) + 1
    else:
        current_page = pages - int(count/5)

    if count == 0:
        update.message.reply_text(
            'متأسفانه پستی یافت نشد', reply_markup=start_markup)
        return SELECTING_ACTION
    if count <= 5:
        for post in context.user_data['all_posts'][0:count]:
            update.message.reply_text(
                prettify(post), parse_mode=ParseMode.MARKDOWN)
            context.user_data['all_posts'] = []
        update.message.reply_text("{0} پست یافت شد \n\n"
                                  "صفحه {1} از {2} \n\n"
                                  "شماره های {3} تا {4}".format(
                                      context.user_data['posts_count'], current_page, pages, (current_page-1)*5 + 1, context.user_data['posts_count']))
        update.message.reply_text(
            'لطفا انتخاب کنید: \n برای دسترسی به بخش مدیریت /admin را ارسال کنید', reply_markup=start_markup)
        return SELECTING_ACTION
    else:
        for post in context.user_data['all_posts'][0:5]:
            update.message.reply_text(
                prettify(post), parse_mode=ParseMode.MARKDOWN)
        context.user_data['all_posts'] = context.user_data['all_posts'][5:]
        update.message.reply_text("{0} پست یافت شد \n\n"
                                  "صفحه {1} از {2} \n\n"
                                  "شماره های {3} تا {4}".format(
                                      context.user_data['posts_count'], current_page, pages, (current_page-1)*5 + 1, current_page*5), reply_markup=reply_markup)
        return GET_POSTS


def prettify(post):
    prettier = "نام کانال: {0} \n\n"\
        "[مشاهده پست در کانال]({1}) \n\n"\
        "تعداد ویو: {2} \n\n"\
        "کپشن: \n {3} \n\n".format(
            post['channel_name'], post['url'], post['views'], post['caption'])
    return prettier
