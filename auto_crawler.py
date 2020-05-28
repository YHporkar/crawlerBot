import datetime
import time
import sched

from models import Channel, Post

from crawler import get_last_post_url, is_there_post, get_post_elements, float_to_int, get_soup, get_date


s1 = sched.scheduler(time.time, time.sleep)


def crawl_channels(channels):
    print(datetime.datetime.now().time(), ' Updating...')
    for channel in channels:
        index = 1
        print(channel.username)
        post_store = []
        post_store = Post.get_urls_by_channel(
            channel.username.replace('@', ''))
        # print(post_store)
        root_url = 'https://t.me/' + channel.username.replace('@', '') + '/'
        start = Channel.update_start(
            channel, get_last_post_url(channel.username))
        i = start
        while(i >= start - index and i != 0):
            print(root_url + str(i))
            # if post is not already in database
            if root_url + str(i) in post_store:
                print('duplicate')
                i -= 1
                continue
            soup = get_soup(root_url + str(i))
            if is_there_post(soup):
                elements = get_post_elements(soup)
                # store in database
                Post(caption=elements['caption'], channel_name=channel.name, views=float_to_int(
                    elements['views']), url=root_url + str(i), date=get_date(soup)).add()
                print(elements)

                # skip album posts
                if elements['lai'] > 0:
                    i -= i - elements['lai']
                    index += i - elements['lai']
            time.sleep(0.5)
            i -= 1

    s1.enter(3600, 1, crawl_channels, (channels,))
    print(datetime.datetime.now().time(), ' Everything is up to date.')


s1.enter(0, 1, crawl_channels, (Channel.get_all(),))

s1.run()
