# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from hazm import Normalizer, sent_tokenize, word_tokenize, Stemmer

import re
import datetime
import time

from models import Post, post_format

from telegram.utils.helpers import effective_message_type


normalizer = Normalizer()
stemmer = Stemmer()

with open('stopwords', 'r', encoding='utf-8') as file:
    sw = file.readlines()
sw = [x.strip() for x in sw]


def remove_emoji(string):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)


def float_to_int(num):
    if 'K' in num:
        num = int(float(num.replace('K', ''))*1000)
    elif 'M' in num:
        num = int(float(num.replace('M', ''))*1000000)
    return num


def get_soup(url):
    html = requests.get(url + '?embed=1')
    soup = BeautifulSoup(html.text, "html.parser")

    return soup


def is_there_post(soup):
    try:
        post = soup.find(
            'div', {'class': 'tgme_widget_message js-widget_message'}).get('data-post')
        if post:
            return True
        return False
    except AttributeError:
        return False


def is_grouped(soup):
    grouped = soup.find(
        'div', {'class': 'tgme_widget_message_grouped_wrap js-message_grouped_wrap'})
    if grouped:
        return True
    return False


def get_album_last_index(soup):
    last_album_index = 0
    # https://t.me/varzesh3/107498?single and last_album_index is 107498
    links = soup.find_all('a')
    album_links = []
    for link in links:
        if link.get('href').__contains__('?single'):
            album_links.append(link.get('href'))
    try:
        last_album_index = int(
            re.search(r'\/[0-9]+', album_links[0]).group(0).replace('/', ''))
    except IndexError:
        return last_album_index

    # data_post = soup.find(
    #     'div', {'class': 'tgme_widget_message js-widget_message'}).get('data-post')

    return last_album_index


def get_caption(soup):
    try:
        for br in soup.find_all('br'):
            br.replace_with('\n')
        caption = soup.find(
            'div', {'class': 'tgme_widget_message_text js-message_text'}).get_text()
    except AttributeError:
        caption = ''

    subs = '[]`*()_'
    for s in subs:
        caption = caption.replace(s, '\\'+s)
    return caption


def get_views(soup):
    try:
        return soup.find('span', {'class': 'tgme_widget_message_views'}).get_text()
    except AttributeError:
        return '0'


def get_date(soup):
    mydatetime = soup.find('time', {'class': 'datetime'}).get('datetime')
    return datetime.datetime.strptime(mydatetime[0:10], '%Y-%m-%d').date()


def get_format(soup):
    if is_grouped(soup):
        return 'album'
    aes = []
    for a in soup.find_all('a'):
        if a.has_attr('class'):
            aes.append(a)
    link_class = aes[-3]['class'][0]
    if link_class.__contains__('photo'):
        return 'photo'
    elif link_class.__contains__('voice'):
        return 'voice'
    elif link_class.__contains__('owner'):
        return 'text'
    elif link_class.__contains__('poll'):
        return 'poll'
    elif link_class.__contains__('video'):
        if soup.find('time', {'class': 'message_video_duration js-message_video_duration'}):
            return 'video'
        return 'animation'
    elif link_class.__contains__('document'):
        if soup.find('div', {'class': 'tgme_widget_message_document_icon'}):
            return 'document'
        return 'audio'
    elif link_class.__contains__('media'):
        return 'sticker'
    elif link_class.__contains__('link_preview'):
        return 'text_link'

# photo 2 -3 has reply
# print(get_format(get_soup('https://t.me/varzesh3/108997')))
# video animation 1 -3
# print(get_format(get_soup('https://t.me/varzesh3/109009')))
# print(get_format(get_soup('https://t.me/varzesh3/108970')))  # document audio 1 -3
# print(get_format(get_soup('https://t.me/kanunbvb/29598')))  # voice 1 -3
# sticker 1 -3 message_media_view_in_telegram
# print(get_format(get_soup('https://t.me/farsna/195224')))
# print(get_format(get_soup('https://t.me/kanunbvb/29594')))  # poll 1 -3

# print(get_format(get_soup('https://t.me/kanunbvb/29545')))
# text 0 -3 tgme_widget_message_owner_name


# print(get_format(get_soup('https://t.me/ahmadmoosavi_ir/464')))

# print(get_format(get_soup('https://t.me/farsna/195364')))  # album


def get_duration(soup):
    if get_format(soup) == 'video':
        return soup.find('time', {'class': 'message_video_duration js-message_video_duration'}).get_text()
    elif get_format(soup) == 'voice':
        return soup.find('time', {'class': 'tgme_widget_message_voice_duration js-message_voice_duration'}).get_text()
    return '0'


def get_post_elements(soup):
    elements = {}
    if is_grouped(soup):
        elements.update({'date': get_date(soup), 'caption': get_caption(
            soup), 'lai': get_album_last_index(soup), 'views': get_views(soup), 'format': get_format(soup), 'duration': get_duration(soup)})
    else:
        elements.update({'date': get_date(soup), 'caption': get_caption(
            soup), 'lai': 0, 'views': get_views(soup), 'format': get_format(soup), 'duration': get_duration(soup)})

    return elements


def arrange_words(words):
    arranged_words = {'and': [], 'or': []}
    for word in words:
        if word.name.__contains__(' '):
            arranged_words['and'].extend(word.name.split('،'))
        else:
            arranged_words['or'].append(word.name)
    return arranged_words


def caption_normalization(caption):
    caption = normalizer.normalize(remove_emoji(caption))
    sent_tokenized_caption = sent_tokenize(caption)
    word_tokenized_caption = []
    for sentense in sent_tokenized_caption:
        word_tokenized_caption.extend(word_tokenize(sentense))
    main = " "
    for w in word_tokenized_caption:
        if not w in sw:
            main += w + " "

    return main


def get_last_post_url(channel_username):
    channel_soup = get_soup(
        'https://t.me/s/' + channel_username.replace('@', '') + '/')
    try:
        return int(re.search(r'\/\d+', channel_soup.find_all('div', {'class': 'tgme_widget_message force_userpic js-widget_message'})[-1].get('data-post')).group(0).replace('/', ''))
    except IndexError:
        return 0


def get_channel_name(channel_username):
    channel_soup = get_soup(
        'https://t.me/s/' + channel_username.replace('@', '') + '/')
    return channel_soup.find('div', {'class': 'tgme_header_title'})


def get_matched_posts_database(query, end_date):
    posts = []
    for post in Post.get_by_query(query, end_date):
        posts.append({'url': post.url, 'caption': post.caption,
                      'channel_name': post.channel_name, 'views': float_to_int(str(post.views)), 'format': post.format,
                      'duration': post.duration, 'datetime': post.date})

    return posts
