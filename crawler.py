from bs4 import BeautifulSoup
import requests
import re
import datetime
import time

# from models import Post


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


# print(is_there_post(get_soup('https://t.me/varzesh3/107557')))


def is_grouped(soup):
    grouped = soup.find(
        'div', {'class': 'tgme_widget_message_grouped_wrap js-message_grouped_wrap'})
    if grouped:
        return True
    return False


def get_album_last_index(soup):
    last_album_index = 0
    # https://t.me/varzesh3/107498?single and last_album_index is 107498
    if is_grouped(soup):
        last_album_index = int(re.search(r'\/[0-9]+', soup.find_all(
            'a', {'class': 'tgme_widget_message_photo_wrap grouped_media_wrap blured js-message_photo'})[0].get('href')).group(0).replace('/', ''))

    return last_album_index


def get_caption(soup):
    try:
        for br in soup.find_all('br'):
            br.replace_with('\n')
        caption = soup.find(
            'div', {'class': 'tgme_widget_message_text js-message_text'}).get_text()
    except AttributeError:
        caption = ''

    return caption


def get_date(soup):
    mydatetime = soup.find('time', {'class': 'datetime'}).get('datetime')
    return datetime.datetime.strptime(mydatetime[0:10], '%Y-%m-%d').date()


def get_post_elements(soup):
    elements = {}
    elements.update({'date': get_date(soup), 'caption': get_caption(
        soup), 'lai': get_album_last_index(soup)})

    return elements


# get_post_elements('https://t.me/varzesh3/107257')
# print(get_caption(get_soup('https://t.me/farsna/192508')))


def check_match(caption, words):
    raw_caption = re.sub(r'[!@#()_=+?\.,،»«:\']+', '', caption)
    for word in words:
        if word in raw_caption:
            return True


def get_matched_posts(channel, words, end_date):
    posts = []

    # database_posts = Post.get_all()
    # for post in database_posts:
    #     if check_match(post.caption):
    #         posts.append(post)

    # url-e.g: https://t.me/varzesh3/107254
    channel_username = channel.get('username')
    start = channel.get('start')

    root_url = 'https://t.me/' + channel_username + '/'

    soup = get_soup(root_url + str(start))

    date = get_date(soup)

    while date >= end_date:
        print(root_url + str(start))
        if is_there_post(soup):
            elements = get_post_elements(soup)
            print(elements)

            if check_match(elements['caption'], words):
                posts.append({'url': root_url + str(start),
                              'caption': elements['caption'], 'channel_name': channel.get('channel_name')})
                print('added')

            # skip album additional urls
            if elements['lai'] > 0:
                start -= start - elements['lai'] + 2
            else:
                start -= 1
            date = elements['date']
        else:
            start -= 1
        soup = get_soup(root_url + str(start))
    return posts


def automatic_save_posts(channels):
    posts = []
    for channel in channels:
        channel_username = channel.get('username')
        start = channel.get('start') + 1
        no_post = 0

        root_url = 'https://t.me/' + channel_username + '/'

        soup = get_soup(root_url + str(start))

        while no_post < 2:
            print(root_url + str(start))
            if is_there_post(soup):
                no_post = 0
                elements = get_post_elements(soup)
                print(elements)
                posts.append({'url': root_url + str(start),
                              'caption': elements['caption'], 'channel_name': channel.get('channel_name')})

                # skip album additional urls
                if elements['lai'] > 0:
                    start += start - elements['lai']
                else:
                    start += 1
            else:
                no_post += 1
                start += 1
            soup = get_soup(root_url + str(start))

    # store in database
    # for post in posts:
    #     Post.add(caption=post['caption'],
    #              channel_name=post['channel_name'], link=post['url'])


# automatic_save_posts(channels)
