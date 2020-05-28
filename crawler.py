# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re

import datetime
import time

from models import Post


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
    last_album_index = int(
        re.search(r'\/[0-9]+', album_links[0]).group(0).replace('/', ''))

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


def get_post_elements(soup):
    elements = {}
    if is_grouped(soup):
        elements.update({'date': get_date(soup), 'caption': get_caption(
            soup), 'lai': get_album_last_index(soup), 'views': get_views(soup)})
    else:
        elements.update({'date': get_date(soup), 'caption': get_caption(
            soup), 'lai': 0, 'views': get_views(soup)})

    return elements


def arrange_words(words):
    arranged_words = {'and': [], 'or': []}
    for word in words:
        if word.name.__contains__('،'):
            arranged_words['and'].extend(word.name.split('،'))
        # elif word.__contains__('-'):
        #     arranged_words['not'].append(word.replace('-', ''))
        else:
            arranged_words['or'].append(word.name)
    return arranged_words


def check_match(caption, words):
    raw_caption = re.sub(r'[!@#()_=+?\.,،»«:\-\']+', ' ', caption)
    or_matched, and_matched = False, False
    if words['or'] != []:
        for or_word in words['or']:
            if or_word in raw_caption:
                or_matched = True
                break
            else:
                or_matched = False

    if words['and'] != []:
        for and_word in words['and']:
            if and_word in raw_caption:
                and_matched = True
            else:
                and_matched = False
                break

    # if words['not'] != []:
    #     for not_word in words['not']:
    #         if not not_word in raw_caption:
    #             not_matched = True
    #         else:
    #             not_matched = False
    # print(or_matched, and_matched)

    if or_matched or and_matched:
        return True
    return False


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


def get_matched_posts(channel, words, end_date):
    posts = []

    # url-e.g: https://t.me/varzesh3/107254

    root_url = 'https://t.me/' + channel.username.replace('@', '') + '/'
    start = channel.start

    soup = get_soup(root_url + str(start))

    date = get_date(soup)

    while date >= end_date:
        print(root_url + str(start))
        if is_there_post(soup):
            elements = get_post_elements(soup)
            print(elements)

            if check_match(elements['caption'], arrange_words(words)):
                posts.append({'url': root_url + str(start),
                              'caption': elements['caption'], 'channel_name': channel.name, 'views': float_to_int(elements['views'])})
                print('added')

            # skip album additional urls
            if elements['lai'] > 0:
                start -= start - elements['lai'] + 1
            else:
                start -= 1
            date = elements['date']
        else:
            start -= 1
        soup = get_soup(root_url + str(start))
        time.sleep(0.1)
    return posts


def get_matched_posts_database(words, end_date):
    posts = []
    words = arrange_words(words)
    for post in Post.get_by_date(end_date):
        if check_match(post.caption, words):
            posts.append({'url': post.url, 'caption': post.caption,
                          'channel_name': post.channel_name, 'views': float_to_int(str(post.views))})

    return posts
